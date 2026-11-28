"""
Simplified TripAdvisor-style trip-planning agent.

Original inspiration (much more complex): ../../../24_tripadvisor_langgraph_poc
and ../../../25_tripadvisor_parallel_gui -- a real TripAdvisor API key + Azure
OpenAI (Foundry) + a ThreadPoolExecutor for manual parallelism + a full
FastAPI/Server-Sent-Events/Docker frontend.

This version keeps the same CONCEPT -- route a travel question to one or more
specialist "agents" (hotel, restaurant, review), then merge their answers --
but strips out everything that isn't the actual lesson:
- Groq instead of Azure OpenAI (one API key, matches the rest of this course)
- Canned/mocked place data instead of a real TripAdvisor API key
- LangGraph's own NATIVE parallel fan-out (a conditional edge that returns a
  LIST of destination node names) instead of a manual ThreadPoolExecutor
- One plain script -- no FastAPI, no SSE, no Docker, no frontend

Run:
    uv run python trip_planner.py
"""
import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph

llm = init_chat_model("groq:qwen/qwen3.8-27b")


class TravelState(TypedDict):
    question: str
    route: list[str]
    city: str
    hotel_result: str
    restaurant_result: str
    review_result: str
    final_answer: str


HOTELS = {
    "paris": "Hotel Lumiere Rive Gauche -- boutique, 4-star, walkable to the Louvre.",
    "tokyo": "Shinjuku Skyline Inn -- modern, 3-star, right next to the station.",
    "goa": "Palm Grove Beach Resort -- 4-star, beachfront, good off-season rates.",
}
RESTAURANTS = {
    "paris": "Le Petit Bistro -- classic French, mid-range, reserve ahead on weekends.",
    "tokyo": "Ichiran Ramen Shinjuku -- solo-booth ramen, no reservation needed.",
    "goa": "Fisherman's Wharf -- seafood, beachside, best at sunset.",
}
REVIEWS = {
    "paris": "4.3/5 average -- travelers love the walkability, complain about summer crowds.",
    "tokyo": "4.6/5 average -- praised for cleanliness and transit access.",
    "goa": "4.1/5 average -- great beaches, mixed reviews on monsoon-season service.",
}


def _lookup(data: dict[str, str], city: str) -> str:
    return data.get(city.lower().strip(), f"No data on file for '{city}' -- try Paris, Tokyo, or Goa.")


def route_node(state: TravelState) -> TravelState:
    """One LLM call does two jobs: pick which specialist(s) to run, AND
    pull out the city -- so the specialist nodes below can be plain,
    fast dictionary lookups with no LLM call of their own."""
    prompt = (
        "You are a travel-question router. Reply with EXACTLY two lines, nothing else.\n"
        "Line 1: a comma-separated list chosen from hotel, restaurant, review "
        "(use all three if it's a general trip-planning question).\n"
        "Line 2: just the city name mentioned in the question.\n\n"
        f"Question: {state['question']}"
    )
    lines = llm.invoke(prompt).content.strip().split("\n")
    categories = [c.strip().lower() for c in lines[0].split(",") if c.strip() in {"hotel", "restaurant", "review"}]
    city = lines[1].strip() if len(lines) > 1 else ""
    return {**state, "route": categories or ["hotel", "restaurant", "review"], "city": city}


def hotel_node(state: TravelState) -> TravelState:
    return {**state, "hotel_result": _lookup(HOTELS, state["city"])}


def restaurant_node(state: TravelState) -> TravelState:
    return {**state, "restaurant_result": _lookup(RESTAURANTS, state["city"])}


def review_node(state: TravelState) -> TravelState:
    return {**state, "review_result": _lookup(REVIEWS, state["city"])}


def final_node(state: TravelState) -> TravelState:
    parts = []
    if state.get("hotel_result"):
        parts.append(f"Hotel: {state['hotel_result']}")
    if state.get("restaurant_result"):
        parts.append(f"Restaurant: {state['restaurant_result']}")
    if state.get("review_result"):
        parts.append(f"Reviews: {state['review_result']}")
    return {**state, "final_answer": "\n".join(parts)}


def choose_routes(state: TravelState) -> list[str]:
    # Returning a LIST of node names here is what triggers LangGraph's
    # native fan-out: all listed nodes run in the same superstep, in
    # parallel, with zero threading code of our own.
    return state["route"]


builder = StateGraph(TravelState)
builder.add_node("router", route_node)
builder.add_node("hotel", hotel_node)
builder.add_node("restaurant", restaurant_node)
builder.add_node("review", review_node)
builder.add_node("final", final_node)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", choose_routes, ["hotel", "restaurant", "review"])
builder.add_edge("hotel", "final")
builder.add_edge("restaurant", "final")
builder.add_edge("review", "final")
builder.add_edge("final", END)

graph = builder.compile()


if __name__ == "__main__":
    questions = [
        "What's a good hotel in Tokyo?",
        "Plan my trip to Goa -- I need a hotel, a place to eat, and how good the reviews are.",
    ]
    for question in questions:
        print(f"\nQ: {question}")
        result = graph.invoke({"question": question})
        print(result["final_answer"])


# --- Reflection questions ---
# 1. `choose_routes` returns a LIST of node names instead of a single one.
#    Compare this to `2_graph_with_condition.ipynb`, where the router
#    returned exactly one branch name. What's different about how
#    LangGraph executes a conditional edge that returns a list versus
#    one that returns a single string?
# 2. The original project used a `ThreadPoolExecutor` inside a single node
#    to run three agents "in parallel" by hand. This version gets the same
#    parallel behavior with zero threading code. What is LangGraph actually
#    doing differently that makes manual threads unnecessary here?
# 3. The router makes ONE LLM call that returns both the routing decision
#    AND the extracted city, so the three specialist nodes never call an
#    LLM at all. What would you lose (or gain) if each specialist node
#    made its own LLM call instead, the way the original project's agents did?
