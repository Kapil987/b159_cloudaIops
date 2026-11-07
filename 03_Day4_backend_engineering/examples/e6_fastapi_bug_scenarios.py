"""
Example 3 — FastAPI live scenarios (a real server, hit real endpoints).

Run:
    uv run uvicorn examples.e6_fastapi_bug_scenarios:app --reload

Then open http://127.0.0.1:8000/docs and try each scenario below, or use
curl. For each: read the docstring, PREDICT the response, then try it.
"""
import time
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Day 3 — FastAPI bug scenarios")


class Movie(BaseModel):
    id: int
    title: str
    genre: str


watchlist: List[Movie] = []


# ---------------------------------------------------------------------------
# Scenario 1 — The silently wrong type, over HTTP
#
# PREDICT: POST {"id": "5", "title": "Inception", "genre": "Sci-Fi"} (id
# as a string) — does this succeed or fail? Now try {"id": "5abc", ...}
# — what does the 422 response body actually look like?
#
# curl — id as a string "5" (Pydantic coerces it to int, succeeds):
#   curl -s -X POST http://127.0.0.1:8000/movies \
#        -H "Content-Type: application/json" \
#        -d '{"id": "5", "title": "Inception", "genre": "Sci-Fi"}'
#
# curl — id as "5abc" (not coercible to int, expect 422):
#   curl -s -X POST http://127.0.0.1:8000/movies \
#        -H "Content-Type: application/json" \
#        -d '{"id": "5abc", "title": "Inception", "genre": "Sci-Fi"}'
#
# curl — GET all movies:
#   curl -s http://127.0.0.1:8000/movies
# ---------------------------------------------------------------------------
@app.post("/movies")
def add_movie(movie: Movie):
    watchlist.append(movie)
    return movie


@app.get("/movies")
def get_movies():
    return watchlist


# ---------------------------------------------------------------------------
# Scenario 2 — The bug hiding in plain sight
#
# This intentionally reproduces the exact bug from main.py: it assigns
# `update_movie` (the FUNCTION itself) into the list instead of
# `updated_movie` (the new Movie object the caller sent).
#
# PREDICT: POST a movie, then PUT an update to it, then GET the list.
# Pydantic validated everything correctly on the way in — will the GET
# show your update?
#
# Step 1 — add a movie first (if not already done via Scenario 1):
#   curl -s -X POST http://127.0.0.1:8000/movies \
#        -H "Content-Type: application/json" \
#        -d '{"id": 1, "title": "Inception", "genre": "Sci-Fi"}'
#
# Step 2 — update it (PUT returns the updated_movie, but list stores the function):
#   curl -s -X PUT http://127.0.0.1:8000/movies/1 \
#        -H "Content-Type: application/json" \
#        -d '{"id": 1, "title": "Inception (Updated)", "genre": "Thriller"}'
#
# Step 3 — GET and inspect the list to see the bug:
#   curl -s http://127.0.0.1:8000/movies
# ---------------------------------------------------------------------------
@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, updated_movie: Movie):
    for index, movie in enumerate(watchlist):
        if movie.id == movie_id:
            watchlist[index] = update_movie  # BUG: should be `updated_movie`
            return updated_movie
    return {"error": "Movie not found"}


# ---------------------------------------------------------------------------
# Scenario 3 — Missing vs. extra field, over HTTP
#
# PREDICT: POST without "genre" vs. POST with an extra "rating" field —
# do you get the same status code both times? Compare the response
# bodies side by side.
#
# curl — missing required field "genre" (expect 422):
#   curl -s -X POST http://127.0.0.1:8000/movies/strict-demo \
#        -H "Content-Type: application/json" \
#        -d '{"id": 10, "title": "Dune"}'
#
# curl — extra unknown field "rating" (Pydantic v2 ignores it by default, succeeds):
#   curl -s -X POST http://127.0.0.1:8000/movies/strict-demo \
#        -H "Content-Type: application/json" \
#        -d '{"id": 11, "title": "Dune", "genre": "Sci-Fi", "rating": 9.5}'
# ---------------------------------------------------------------------------
@app.post("/movies/strict-demo")
def add_movie_strict_demo(movie: Movie):
    # Same model as add_movie — this endpoint exists only so you can
    # point at it separately when comparing the two failure modes
    # without polluting the main /movies list used in Scenario 2.
    return movie


# ---------------------------------------------------------------------------
# Scenario 4 — The blocking endpoint in a crowd
#
# Same pattern as examples/e4_async_sync.py's /1 endpoint. Open 2+
# terminals and curl this concurrently:
#     curl http://127.0.0.1:8000/slow
# Watch the server terminal's printed order, not the HTTP responses.
#
# PREDICT: with 2 concurrent requests, does the 2nd request's "hello"
# print before or after the 1st request's "bye"?
#
# curl — single request (takes ~5 s):
#   curl -s http://127.0.0.1:8000/slow
#
# curl — two concurrent requests (open two terminals and run simultaneously):
#   Terminal 1:  curl -s http://127.0.0.1:8000/slow
#   Terminal 2:  curl -s http://127.0.0.1:8000/slow
#
# One-liner to fire both at once (Linux/Mac/Git Bash):
#   curl -s http://127.0.0.1:8000/slow & curl -s http://127.0.0.1:8000/slow; wait
# ---------------------------------------------------------------------------
@app.get("/slow")
async def slow_endpoint():
    print("hello")
    time.sleep(5)  # blocking call inside async def — the anti-pattern
    print("bye")
    return {"message": "done"}
