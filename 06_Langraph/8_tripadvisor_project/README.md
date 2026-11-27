# TripAdvisor Trip Planner — Simplified

A much smaller version of the `24_tripadvisor_langgraph_poc` /
`25_tripadvisor_parallel_gui` projects elsewhere in this repo, built for
this course. Same core idea — route a travel question to one or more
specialist agents (hotel, restaurant, review), then merge their answers —
with everything that isn't the actual lesson stripped out.

## What's simpler here, and why

| Original project | This version | Why |
|---|---|---|
| Real TripAdvisor API key + Azure OpenAI (Foundry) | Groq only, canned place data (Paris/Tokyo/Goa) | One API key, matches the rest of this course, zero extra signup |
| Manual `ThreadPoolExecutor` to run 3 agents "in parallel" | LangGraph's own native fan-out (a conditional edge returning a *list* of node names) | No threading code to write or debug — LangGraph does this for you |
| Full FastAPI app + Server-Sent Events + Docker + static frontend | One plain Python script | The lesson is the *graph*, not the web app around it |
| 3 separate LLM calls (one per specialist agent) | 1 LLM call total (router picks the route AND extracts the city; specialists are plain dict lookups) | Fewer moving parts, faster, and it separates "the LLM decides" from "code executes" — same split you already saw in `4_tool_call.ipynb` |

## Setup

```bash
uv sync
```

Copy `.env.example` to `.env` and add your Groq key:
```env
GROQ_API_KEY=your_groq_key
```

## Run

```bash
uv run python trip_planner.py
```

You should see two example questions run — one that only needs the hotel
specialist, and one general "plan my trip" question that fans out to all
three specialists at once, then merges into a final combined answer.

## Where this fits

This sits right after `7_HITL.py` — it's a chance to combine conditional
routing (`2_graph_with_condition.ipynb`), tool-style lookups
(`4_tool_call.ipynb`), and parallel fan-out (new here) into one small
project, before moving on to `07_Observability_Evaluation_Authentication`.
