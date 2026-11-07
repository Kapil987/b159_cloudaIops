"""
Example 2 — FastAPI from scratch, with plain dicts (no Pydantic models yet).

FastAPI's job is to turn Python functions into HTTP endpoints. This file
deliberately skips Pydantic models so you see FastAPI's own job in
isolation: routes, path parameters, query parameters, and request bodies
as plain dicts. Example 3 puts Pydantic back in and shows why you want it.

Run:
    uv run uvicorn examples.e2_fastapi_basics:app --reload

Then open http://127.0.0.1:8000/docs for interactive testing, or use curl.
"""
from fastapi import FastAPI

app = FastAPI(title="Example 2 — FastAPI basics")


# ---------------------------------------------------------------------------
# Step 1 — the smallest possible endpoint
#
# @app.get(path) + a function = a route. FastAPI calls this function
# whenever a GET request hits "/", and turns whatever it returns into a
# JSON response automatically.
#
# Try: curl http://127.0.0.1:8000/
# Decorators in Python are functions that modify or extend the behaviour of another function without changing its original code
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "hello from FastAPI"}


# ---------------------------------------------------------------------------
# Step 2 — path parameters
#
# `{movie_id}` in the path becomes a function argument. FastAPI reads it
# straight out of the URL — no manual parsing.
#
# Try: curl http://127.0.0.1:8000/movies/7
# Browser path parameters arrive as strings, but FastAPI converts them to integers because of the movie_id: int type annotation.
# ---------------------------------------------------------------------------
@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    print(type(movie_id))
    # print(type(str(type(movie_id))))
    return {"movie_id": movie_id, "type_in_python": str(type(movie_id))}
    # return {"movie_id": movie_id, "type_in_python": type(movie_id)}


# ---------------------------------------------------------------------------
# Step 3 — path parameter TYPE matters
#
# `movie_id: int` isn't just a hint — FastAPI enforces it. A non-numeric
# value never reaches your function at all.
#
# Try: curl http://127.0.0.1:8000/movies/abc
# Compare the error against Step 2's success.
# ---------------------------------------------------------------------------
# (same endpoint as Step 2 — re-read it with this in mind)


# ---------------------------------------------------------------------------
# Step 4 — query parameters
#
# Function arguments that do NOT appear in the path (like `genre` here)
# become query parameters instead: ?genre=Sci-Fi
# "Any" is the default value of the genre parameter.
# Try: curl "http://127.0.0.1:8000/search?genre=Sci-Fi"
# Try:  curl "http://127.0.0.1:8000/search"   (genre has a default, so it's optional)
# ---------------------------------------------------------------------------
@app.get("/search")
def search_movies(genre: str = "Any"):
    return {"searching_for_genre": genre}


# ---------------------------------------------------------------------------
# Step 5 — a request body, as a plain dict
#
# POST requests usually carry a JSON body. Without Pydantic, you can
# still receive it as a plain dict — but nothing validates its shape.
# Send garbage and FastAPI won't stop you; your function just gets it.
#
# Try:
#   curl -X POST http://127.0.0.1:8000/movies-raw \
#        -H "Content-Type: application/json" \
#        -d '{"anything": "goes", "id": "not-even-a-number"}'
# ---------------------------------------------------------------------------
@app.post("/movies-raw")
def add_movie_raw(movie: dict):
    return {"you_sent": movie, "note": "no validation happened — this is the problem Example 3 fixes"}


# ---------------------------------------------------------------------------
# Rule of thumb for this file
#
# FastAPI wires HTTP -> Python function -> HTTP, and enforces simple
# path/query param types for you. It does NOT validate the *shape* of a
# JSON body on its own — that's Pydantic's job, coming up next.
# ---------------------------------------------------------------------------
