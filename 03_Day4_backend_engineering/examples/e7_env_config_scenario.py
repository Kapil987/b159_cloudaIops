import os
from dotenv import load_dotenv


load_dotenv()

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
    # port = int(port)  # <-- this line is doing ALL the real validation

    print("Manual config loaded (if we got here, no exception was raised).")
    return {
        "api_key": api_key,
        "database_url": database_url,
        "port": port
    }



if __name__ == "__main__":
    manual = load_config_manually()
    print(manual)


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
