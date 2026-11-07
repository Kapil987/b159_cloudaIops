"""
Example 3 — FastAPI + Pydantic together: a minimal Movie Watchlist API.

Example 1 showed Pydantic validating plain Python objects. Example 2
showed FastAPI routing HTTP requests with no validation on the body.
This file puts them together — the combination is what `main.py` (the
full watchlist API) is built from.

Run:
    uv run uvicorn examples.e3_fastapi_pydantic_combined:app --reload

Then open http://127.0.0.1:8000/docs for interactive testing, or use curl.
"""
# from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Example 3 — FastAPI + Pydantic combined")


# ---------------------------------------------------------------------------
# Step 1 — the shared model
#
# Same BaseModel pattern as e1_pydantic_basics.py. The difference here is
# WHERE it gets used: as a type annotation on an endpoint's parameter.
# ---------------------------------------------------------------------------
class Movie(BaseModel):
    id: int
    title: str
    genre: str


# watchlist: List[Movie] = [] is called a type annotation (type hint) in Python.
# It tells Python developers and tools what kind of data the variable is expected to hold.

watchlist: list[Movie] = []  # in-memory storage — resets every server restart


# ---------------------------------------------------------------------------
# Step 2 — `movie: Movie` as a parameter means "validate the request body
# against this shape before my function even runs"
#
# Compare this to e2_fastapi_basics.py's `add_movie_raw(movie: dict)` —
# same idea (a POST body), but now it's enforced.
#
# Try (valid):
#   curl -X POST http://127.0.0.1:8000/movies \
#        -H "Content-Type: application/json" \
#        -d '{"id": 1, "title": "Inception", "genre": "Sci-Fi"}'
#
# Try (invalid — id is not a number-like value):
#   curl -X POST http://127.0.0.1:8000/movies \
#        -H "Content-Type: application/json" \
#        -d '{"id": "abc", "title": "Inception", "genre": "Sci-Fi"}'
#
# The second one never reaches this function's body at all — FastAPI
# rejects it with a 422 before your code runs.
# ---------------------------------------------------------------------------
@app.post("/movies")
def add_movie(movie: Movie):
    watchlist.append(movie)
    return movie


# ---------------------------------------------------------------------------
# Step 3 — returning a Pydantic model (or a list of them) as the response
#
# FastAPI serializes the Movie objects back to JSON automatically — this
# is Pydantic working on the OUTBOUND side, not just the inbound side.
#
# Try: curl http://127.0.0.1:8000/movies
# ---------------------------------------------------------------------------
@app.get("/movies")
def get_movies():
    return watchlist


# ---------------------------------------------------------------------------
# Step 4 — mixing a path parameter (plain int, like Example 2) with a
# validated body (a Movie, like Step 2) in the same endpoint
#
# Try:
#   curl -X PUT http://127.0.0.1:8000/movies/1 \
#        -H "Content-Type: application/json" \
#        -d '{"id": 1, "title": "Inception (Updated)", "genre": "Sci-Fi"}'
# ---------------------------------------------------------------------------
@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, updated_movie: Movie):
    print('watchlist is',watchlist)
    for index, movie in enumerate(watchlist):
        if movie.id == movie_id:
            watchlist[index] = updated_movie
            return updated_movie
    return {"error": "Movie not found"}


# ---------------------------------------------------------------------------
# Where to go next
#
# `main.py` in this folder is the same pattern with a DELETE endpoint
# added — full CRUD. From there, e5/e6/e7 dig into what can still go
# wrong even with validation in place (logic bugs, edge cases, config).
# ---------------------------------------------------------------------------
