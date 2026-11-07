"""
Example 1 — Pydantic from scratch (no FastAPI, no server).

Pydantic answers one question: "is this data shaped the way I said it
should be?" You define the shape once as a class, and Pydantic checks
every object you create against it.

Run:
    uv run python examples/e1_pydantic_basics.py
"""
from pydantic import BaseModel, ValidationError

# ---------------------------------------------------------------------------
# Step 1 — a plain dict has no rules
#
# Nothing stops you from putting a string where a number belongs. Python
# accepts it happily — the dict is created with no complaint at all.
# app --> LLM/Agent --> response --> dict with id as string !!
# ---------------------------------------------------------------------------
def step_1_plain_dict():
    print("\n=== Step 1: a plain dict has no rules ===")
    movie = {"id": "one", "title": "Inception", "genre": "Sci-Fi"}  # "id" should be a number
    print(f"dict = {movie}")
    print("No error. Python doesn't care that 'id' is the word 'one' instead of a number.")


# ---------------------------------------------------------------------------
# Step 2 — define the shape once, as a class
#
# A BaseModel is a class where every attribute has a declared type.
# Creating an instance now VALIDATES the data against that shape — the
# exact same bad "id" from Step 1 is rejected immediately, right where
# it was created, instead of blowing up later somewhere else.
# ---------------------------------------------------------------------------
class Movie(BaseModel):
    id: int
    title: str
    genre: str


def step_2_valid_model():
    print("\n=== Step 2: Pydantic catches the same bad data immediately ===")
    # try:
    #     Movie(id="one", title="Inception", genre="Sci-Fi") # creates an instance (object) of the Movie class.
    # except ValidationError as e:
    #     print(f"Rejected right at creation — no need to wait for it to break later:\n{e}")

    movie = Movie(id=1, title="Inception", genre="Sci-Fi")
    # print(f"\nWith correct data: movie = {movie!r}")
    # print(f"\nWith correct data: movie = {movie}")
    print(f"movie.title = {movie.title!r} (type: {type(movie.title).__name__})") # str.__name__
    print(f"movie.title = {movie.title!r} (type: {type(movie.title)})") # str.__name__


# ---------------------------------------------------------------------------
# Step 3 — a different kind of invalid data: a missing required field
#
# Step 2 showed a wrong TYPE. This shows a MISSING field entirely —
# Pydantic tells you exactly which field is missing, not just "something's wrong".
# ---------------------------------------------------------------------------
def step_3_invalid_model():
    print("\n=== Step 3: a Movie missing a required field ===")
    try:
        Movie(title="Inception", genre="Sci-Fi")  # no "id" at all
    except ValidationError as e:
        print(f"ValidationError:\n{e}")


# ---------------------------------------------------------------------------
# Step 4 — type coercion: Pydantic tries to convert before rejecting
#
# "5" (a numeric-looking string) becomes the int 5. This is a deliberate
# default behavior, not a bug — useful to know since it means "it didn't
# raise an error" doesn't always mean "the type was exactly right".
# ---------------------------------------------------------------------------
def step_4_coercion():
    print("\n=== Step 4: coercion vs rejection ===")
    movie = Movie(id="5", title="Inception", genre="Sci-Fi")
    print(f"'5' (string) became: {movie.id!r} (type: {type(movie.id).__name__})")


# ---------------------------------------------------------------------------
# Step 5 — optional fields with defaults
#
# Fields with a default value are optional; fields without one are
# required. Leave `genre` out entirely and see the difference.
# ---------------------------------------------------------------------------
class MovieWithDefault(BaseModel):
    id: int
    title: str
    genre: str = "Unknown"


def step_5_defaults():
    print("\n=== Step 5: optional field with a default ===")
    movie = MovieWithDefault(id=2, title="Interstellar")
    print(f"No genre given, default used: {movie!r}")


# ---------------------------------------------------------------------------
# Step 6 — converting to/from dict and JSON
#
# Models convert cleanly to plain Python (.model_dump()) or JSON text
# (.model_dump_json()) — this is exactly what FastAPI uses under the hood
# to turn your models into HTTP responses.
# ---------------------------------------------------------------------------
def step_6_serialization():
    print("\n=== Step 6: model -> dict / JSON ===")
    movie = Movie(id=1, title="Inception", genre="Sci-Fi")
    print(f"model_dump()      -> {movie.model_dump()}")
    print(f"model_dump_json() -> {movie.model_dump_json()}")


# ---------------------------------------------------------------------------
# Bonus — what the crash looks like with NO try/except at all
#
# Step 2 catches the error so the script can keep running through Step 6.
# But you don't need try/except to benefit from validation — Pydantic
# crashes loudly on its own, with a full traceback pointing at the exact
# field and the exact problem. try/except is only for when you want to
# handle the error yourself instead of letting the program stop.
#
# This is commented out of the __main__ list below because an uncaught
# error would stop the script before Steps 3-6 run. To see it for
# yourself, comment out everything else in __main__ and uncomment the
# line below, then run the file again.
# ---------------------------------------------------------------------------
def bonus_uncaught_crash():
    Movie(id="one", title="Inception", genre="Sci-Fi")  # no try/except — this crashes


if __name__ == "__main__":
    # step_1_plain_dict()
    # step_2_valid_model()
    # step_3_invalid_model()
    # step_4_coercion()
    # step_5_defaults()
    # step_6_serialization()

    bonus_uncaught_crash()
