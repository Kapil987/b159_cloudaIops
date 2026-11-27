"""
v1: RAG only.

    START -> rag_agent -> merge -> END

rag_agent  searches the Bedrock Knowledge Base for passages about the question.
merge      asks the LLM to answer from those passages only, and to cite them.

This version is good at "what does the clause say" questions. It is NOT good at
"which contracts expire in the next 90 days": it only sees a few text passages,
not a table of dates. v2 fixes that.
"""
import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `common` can be imported

from langgraph.graph import END, START, StateGraph

from common.kb import label, retrieve
from common.llm import ask


class Input(TypedDict):
    """What the app hands to the graph."""
    question: str
    client_id: str      # set by the app from the login. The LLM never touches it.


class State(Input):
    """Input plus what the agents fill in as the graph runs."""
    passages: list[dict]
    answer: str


def rag_agent(state: State) -> dict:
    """Agent 1: fetch passages from the Knowledge Base, for this client only."""
    return {"passages": retrieve(state["question"], state["client_id"])}


def merge(state: State) -> dict:
    """Turn the passages into one cited answer."""
    passages = state["passages"]
    if not passages:
        return {"answer": "I could not find anything about that in this client's contracts."}

    context = "\n\n".join(f"[{label(p)}]\n{p['text']}" for p in passages)
    prompt = f"""You are an assistant for a law firm's attorneys.
Answer the question using ONLY the contract passages below.
After each fact, cite the contract in square brackets, like [NOV-001 CloudServe Inc].
If the passages do not contain the answer, say so. Do not guess.

Passages:
{context}

Question: {state['question']}"""
    return {"answer": ask(prompt)}


builder = StateGraph(State, input_schema=Input)
builder.add_node("rag_agent", rag_agent)
builder.add_node("merge", merge)
builder.add_edge(START, "rag_agent")
builder.add_edge("rag_agent", "merge")
builder.add_edge("merge", END)
graph = builder.compile()


if __name__ == "__main__":
    # Quick test without Streamlit:  uv run python v1_rag_only/graph.py
    result = graph.invoke({"question": "What does the liability clause say in the CloudServe contract?",
                           "client_id": "nova_foods"})
    print(result["answer"])
