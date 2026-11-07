"""
Example 2 — Pydantic-only scenarios (no FastAPI, no server).

Run:
    uv run python examples/e5_pydantic_scenarios.py

Each scenario: read the docstring, PREDICT the output before scrolling
past the print statements, then run the file and compare.
"""
from pydantic import BaseModel, ConfigDict, ValidationError


# ---------------------------------------------------------------------------
# Scenario 1 — The silently wrong type
#
# Movie.id is typed `int`. What happens if a client sends "5" (a string
# that LOOKS numeric) instead of 5? What about "5abc"?
#
# PREDICT: does Pydantic reject "5abc", or fail differently than "5"?
# ---------------------------------------------------------------------------
class Movie(BaseModel):
    id: int
    title: str
    genre: str


def scenario_1():
    print("\n=== Scenario 1: The silently wrong type ===")

    movie = Movie(id="5", title="Inception", genre="Sci-Fi")  # "5" -> int 5
    print(f"'5' (numeric string) coerced to: {movie.id!r} (type: {type(movie.id).__name__})")

    try:
        Movie(id="5abc", title="Inception", genre="Sci-Fi")
    except ValidationError as e:
        print(f"'5abc' raised ValidationError:\n{e}")


# ---------------------------------------------------------------------------
# Scenario 2 — Missing field vs. extra field
#
# PREDICT: are "missing required field" and "unexpected extra field"
# treated the same way by default?
# ---------------------------------------------------------------------------
def scenario_2():
    print("\n=== Scenario 2: Missing vs. extra field ===")

    print("-- Missing required field ('genre') --")
    try:
        Movie(id=1, title="Interstellar")
    except ValidationError as e:
        print(e)

    print("\n-- Extra unexpected field ('rating') --")
    movie = Movie(id=1, title="Interstellar", genre="Sci-Fi", rating=9.5)
    print(f"No error raised. Extra field silently dropped. movie = {movie!r}")
    print(f"Does movie have a .rating attribute? {hasattr(movie, 'rating')}")


# ---------------------------------------------------------------------------
# Scenario 3 — strict mode changes the answer to Scenario 1
#
# PREDICT: with strict=True, does Movie(id="5", ...) still succeed?
# ---------------------------------------------------------------------------
class StrictMovie(BaseModel):
    model_config = ConfigDict(strict=True)
    id: int
    title: str
    genre: str


def scenario_3():
    print("\n=== Scenario 3: strict=True removes coercion ===")
    try:
        StrictMovie(id="5", title="Inception", genre="Sci-Fi")
    except ValidationError as e:
        print(f"Same '5' that worked in Scenario 1 now fails under strict mode:\n{e}")


# ---------------------------------------------------------------------------
# Scenario 4 — Nested model validation reports the FULL path
#
# PREDICT: if Director.contact.phone is wrong, does the error just say
# "phone is invalid", or does it show the whole path?
# ---------------------------------------------------------------------------
class Contact(BaseModel):
    email: str
    phone: int


class Director(BaseModel):
    name: str
    contact: Contact


def scenario_4():
    print("\n=== Scenario 4: Nested model validation error paths ===")
    try:
        Director(
            name="Christopher Nolan",
            contact={"email": "nolan@example.com", "phone": "not-a-number"},
        )
    except ValidationError as e:
        print(f"Error path shows the full nested location, not just 'phone':\n{e}--")


if __name__ == "__main__":
    # scenario_1()
    # scenario_2()
    # scenario_3()
    scenario_4()
