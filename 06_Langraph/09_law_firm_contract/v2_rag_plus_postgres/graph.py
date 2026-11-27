"""
v2: RAG + Postgres metadata + a router.

    START -> router -+-> rag_agent -------------------------> merge -> END
                     +-> metadata_agent -> merge -> END              (facts only)
                     +-> metadata_agent -> rag_agent -> merge -> END (both)

router          decides what kind of question this is: rag, metadata or both.
metadata_agent  picks one fixed Postgres query (dates, flags, amounts) and runs it.
rag_agent       searches the Knowledge Base for clause wording.
merge           writes one answer from the facts and the passages, with citations.

For "both" the order matters: Postgres first finds WHICH contracts qualify
(for example, renewing in the next 90 days). Only then does RAG read the clauses of
exactly those contracts. So the two agents run one after the other, not in parallel.
"""
import json
import re
import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langgraph.graph import END, START, StateGraph

from common.config import AS_OF_DATE
from common.kb import label, retrieve
from common.llm import ask
from db import TOOLS

ROUTES = ("rag", "metadata", "both")


class Input(TypedDict):
    """What the app hands to the graph."""
    question: str
    client_id: str      # set by the app from the login. The LLM never touches it.


class State(Input):
    """Input plus what the agents fill in as the graph runs."""
    route: str          # "rag" | "metadata" | "both"
    tool_call: dict     # which Postgres query the metadata agent chose (for the trace)
    contracts: list[dict]
    passages: list[dict]
    answer: str


# --- router -------------------------------------------------------------------

def router(state: State) -> dict:
    """Classify the question. The LLM answers with exactly one word."""
    prompt = f"""You route questions from a law-firm attorney about one client's contracts.
Reply with exactly one word:
- metadata: the answer is exact facts only (dates, deadlines, renewal flags, amounts, which contracts exist)
- rag: the answer is only about what the contract wording or a clause says
- both: it needs facts to pick the contracts AND clause wording to judge them

Question: {state['question']}
Reply with one word:"""
    reply = ask(prompt).lower()
    route = next((r for r in ROUTES if r in reply), "both")  # unsure -> do the more complete route
    return {"route": route}


def after_router(state: State) -> str:
    # "both" starts with metadata, because RAG needs the contract list first.
    return "rag_agent" if state["route"] == "rag" else "metadata_agent"


# --- metadata agent (Postgres) --------------------------------------------------

def metadata_agent(state: State) -> dict:
    """Agent 2: let the LLM choose ONE fixed query, then run it with the client filter."""
    prompt = f"""Pick the database query that fetches the contract facts needed for this question.
Today's date is {AS_OF_DATE.isoformat()}.

Queries:
- list_contracts: every contract
- expiring_within: contracts expiring in the next N days (needs "days")
- auto_renewing_within: contracts that auto-renew and expire in the next N days (needs "days")
- find_by_counterparty: contracts with one named company (needs "counterparty")

Reply with JSON only, for example {{"tool": "expiring_within", "days": 90}}

Question: {state['question']}"""
    call = _parse_tool_call(ask(prompt))
    # client_id comes from the login (state), never from the LLM's reply.
    rows = TOOLS[call["tool"]](state["client_id"], AS_OF_DATE, call["days"], call["counterparty"])
    return {"tool_call": call, "contracts": rows}


def _parse_tool_call(reply: str) -> dict:
    """Read the LLM's JSON, and fall back to a safe default if it is malformed."""
    call = {"tool": "list_contracts", "days": 90, "counterparty": ""}
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if data.get("tool") in TOOLS:
                call["tool"] = data["tool"]
            call["days"] = max(1, min(int(data.get("days", 90)), 730))
            call["counterparty"] = str(data.get("counterparty") or "")
        except (ValueError, TypeError):
            pass
    return call


def after_metadata(state: State) -> str:
    # Only go on to RAG when there is something to look at.
    if state["route"] == "both" and state["contracts"]:
        return "rag_agent"
    return "merge"


# --- RAG agent (Bedrock Knowledge Base) ----------------------------------------

def rag_agent(state: State) -> dict:
    """Agent 1: fetch clause passages, limited to the contracts Postgres found (if it ran)."""
    ids = [c["contract_id"] for c in state.get("contracts", [])] or None
    return {"passages": retrieve(state["question"], state["client_id"], ids)}


# --- merge ------------------------------------------------------------------------

def merge(state: State) -> dict:
    contracts = state.get("contracts", [])
    passages = state.get("passages", [])
    if state["route"] != "rag" and not contracts:
        return {"answer": "No contracts match that in this client's records."}
    if state["route"] == "rag" and not passages:
        return {"answer": "I could not find anything about that in this client's contracts."}

    facts = json.dumps(contracts, default=str, indent=1) if contracts else "(none)"
    context = "\n\n".join(f"[{label(p)}]\n{p['text']}" for p in passages) or "(none)"
    prompt = f"""You are an assistant for a law firm's attorneys. Today's date is {AS_OF_DATE.isoformat()}.
Answer the question using ONLY the facts and passages below.
- Dates, amounts and renewal flags come from the FACTS. Clause wording comes from the PASSAGES.
- Cite contracts in square brackets, like [NOV-001 CloudServe Inc].
- When judging a clause such as liability, say which side the client is on if the passage shows it,
  because unlimited liability protects a buyer but is a risk for a seller.
- If something is missing, say so. Do not guess.

FACTS (from the database):
{facts}

PASSAGES (from the contracts):
{context}

Question: {state['question']}"""
    return {"answer": ask(prompt)}


builder = StateGraph(State, input_schema=Input)
builder.add_node("router", router)
builder.add_node("metadata_agent", metadata_agent)
builder.add_node("rag_agent", rag_agent)
builder.add_node("merge", merge)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", after_router, ["rag_agent", "metadata_agent"])
builder.add_conditional_edges("metadata_agent", after_metadata, ["rag_agent", "merge"])
builder.add_edge("rag_agent", "merge")
builder.add_edge("merge", END)
graph = builder.compile()


if __name__ == "__main__":
    # Quick test without Streamlit:  uv run python v2_rag_plus_postgres/graph.py
    for q in ["Which contracts expire in the next 90 days?",
              "What does the liability clause say in the CloudServe contract?",
              "Which contracts auto-renew within 90 days and have unlimited liability?"]:
        result = graph.invoke({"question": q, "client_id": "nova_foods"})
        print(f"\nQ: {q}\nroute: {result['route']}\n{result['answer']}")
