"""
Example 4 — manual if-checks vs. pydantic-settings for .env config,
side by side.

Run:
    uv run python examples/e7_env_config_scenario.py

Same 5 config fields (API_KEY, DATABASE_URL, PORT, DEBUG, MAX_RETRIES)
loaded two ways in one file so you see the difference in one shot
instead of comparing across separate runs. Needs a `.env` file next to
this one (see e7_env_config_scenario.env.example) — copy it to `.env` in
this folder before running.

Try it broken (delete a field from .env, or set PORT to a non-numeric
string) and watch how differently each half of this file reacts.
"""
import os

from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_settings import BaseSettings

load_dotenv()


# ---------------------------------------------------------------------------
# APPROACH 1 — manual if-checks (the way most people start out)
#
# This is not a strawman — this is genuinely how a lot of real projects
# read config, especially early on. Read it top to bottom and count how
# many things it does NOT check for, compared to what it looks like it's
# checking for.
# ---------------------------------------------------------------------------
def load_config_manually() -> dict:
    print("--- Approach 1: manual if-checks ---")

    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY is missing!")

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is missing!")

    # Looks safe. It isn't — os.environ.get() ALWAYS returns a string
    # (or None). "PORT" being "present" tells you nothing about whether
    # it's actually a usable integer.
    port = os.environ.get("PORT")
    if not port:
        raise RuntimeError("PORT is missing!")
    # Did you remember to convert it? Half of manual configs forget this
    # exact line, and nothing here would have caught that until PORT gets
    # used somewhere that requires an int (e.g. binding a socket).
    port = int(port)  # <-- this line is doing ALL the real validation

    # Optional fields with defaults — every one of these needs its own
    # repeated if/else pattern. This is the part that scales badly: 5
    # fields here means 5 near-duplicate blocks; 30 fields in a real app
    # means 30, each one a place a mistake can hide.
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    max_retries = int(os.environ.get("MAX_RETRIES", "3"))

    print("Manual config loaded (if we got here, no exception was raised).")
    return {
        "api_key": api_key,
        "database_url": database_url,
        "port": port,
        "debug": debug,
        "max_retries": max_retries,
    }


# ---------------------------------------------------------------------------
# APPROACH 2 — pydantic-settings (declare the shape once, get validation
# for free)
# ---------------------------------------------------------------------------
class Settings(BaseSettings):
    api_key: str
    database_url: str
    port: int  # <-- just declaring the TYPE is the whole validation rule
    debug: bool = False
    max_retries: int = 3

    class Config:
        env_file = ".env"
        # pydantic-settings matches env var names case-insensitively by
        # default, so API_KEY in .env maps to api_key here automatically.


def load_config_with_pydantic() -> "Settings":
    print("\n--- Approach 2: pydantic-settings ---")
    settings = Settings()
    print("Pydantic config loaded.")
    return settings


if __name__ == "__main__":
    try:
        manual = load_config_manually()
        print(manual)
    except RuntimeError as e:
        print(f"Manual approach failed with: {e}")

    try:
        typed = load_config_with_pydantic()
        print(typed)
    except ValidationError as e:
        print(f"Pydantic approach failed with:\n{e}")


# ---------------------------------------------------------------------------
# THE DEMO — do this live, in order:
#
# 1. Run this file with a correct .env. Both approaches succeed. Looks
#    like a wash so far.
#
# 2. In .env, change PORT="8080" to PORT="eighty-eighty" (a non-numeric
#    string). Re-run.
#      - Manual approach: crashes at `int(port)` with Python's own
#        ValueError ("invalid literal for int() with base 10:
#        'eighty-eighty'") — a generic Python error that doesn't mention
#        PORT, .env, or config AT ALL. You have to already know where to
#        look.
#      - Pydantic approach: raises a ValidationError that explicitly
#        names the field ("port") and explains what it expected.
#
# 3. Now the more dangerous one — in .env, DELETE the PORT line entirely
#    but ALSO change the manual code's `if not port:` line to
#    `port = os.environ.get("PORT", "8080")` (i.e. add a silent default,
#    which is an extremely common "helpful" habit).
#      - Manual approach: doesn't crash at all. Silently uses 8080.
#        If your production .env is genuinely missing PORT because of a
#        deploy mistake, you'll never know — you'll just be running on
#        the wrong port and debugging something else entirely for an
#        hour before you think to check this.
#      - Pydantic approach: still crashes immediately, naming the
#        missing field, because `port: int` with no `= default` means
#        required stays required no matter what.
#
# 4. Ask the room: which failure mode would you rather have at 2am
#    during an incident — a crash that names the exact field, or a
#    silent wrong value that "works" until something downstream breaks
#    in a way that doesn't obviously point back here?
# ---------------------------------------------------------------------------
