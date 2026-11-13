# Day 3 — Backend Engineering (FastAPI + Pydantic)

This folder started as a copy of [`29_fastAPI/`](../../29_fastAPI)'s
structure, retargeted to a **Movie Watchlist API** (instead of the
original tea-house example) **plus** new runnable scenario files added
for teaching. `PROJECT_NOTES.md` is the original project's own README
(async/sync rule-of-thumb notes) — kept as reference, separate from this
lesson doc.

## Run it

```powershell
uv sync
uv run uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000` — interactive docs at
`http://127.0.0.1:8000/docs` (use this for live demos — it's the fastest
way to POST/PUT/DELETE in front of a class without a Postman setup).

## Files

Examples are numbered in teaching order: e1/e2 introduce each tool in
isolation, e3 combines them, e4-e7 go deeper (async internals, edge-case
scenarios, bug-hunting, config). `main.py` is the full CRUD app the whole
sequence builds toward.

- [`examples/e1_pydantic_basics.py`](examples/e1_pydantic_basics.py) —
  **start here**: Pydantic alone, no FastAPI, no server. Defining a
  `BaseModel`, validation errors, type coercion, defaults, serializing
  to dict/JSON. Run directly:
  `uv run python examples/e1_pydantic_basics.py`
- [`examples/e2_fastapi_basics.py`](examples/e2_fastapi_basics.py) —
  FastAPI alone, deliberately using plain `dict` request bodies (no
  Pydantic yet) so you see routing, path params, and query params as
  FastAPI's job in isolation — and see the gap Pydantic fills. Run:
  `uv run uvicorn examples.e2_fastapi_basics:app --reload`
- [`examples/e3_fastapi_pydantic_combined.py`](examples/e3_fastapi_pydantic_combined.py) —
  puts e1 + e2 together: a minimal Movie Watchlist API where `Movie`
  validates both incoming request bodies and outgoing responses. This is
  the pattern `main.py` is built from. Run:
  `uv run uvicorn examples.e3_fastapi_pydantic_combined:app --reload`
- [`main.py`](main.py) — the full Movie Watchlist CRUD API (adds DELETE)
- [`examples/e4_async_sync.py`](examples/e4_async_sync.py) — async vs
  sync endpoints (unchanged from `29_`)
- [`examples/e5_pydantic_scenarios.py`](examples/e5_pydantic_scenarios.py) —
  standalone Pydantic edge-case scenarios (no FastAPI/server needed —
  run directly with `uv run python examples/e5_pydantic_scenarios.py`)
- [`examples/e6_fastapi_bug_scenarios.py`](examples/e6_fastapi_bug_scenarios.py) —
  a second small API with the 4 scenarios below wired in as
  real endpoints to demo live
- [`examples/e7_env_config_scenario.py`](examples/e7_env_config_scenario.py) —
  manual `if`-check config loading vs. `pydantic-settings`,
  side by side in one file — copy
  [`examples/e7_env_config_scenario.env.example`](examples/e7_env_config_scenario.env.example)
  to `.env` in this folder first, then run with
  `uv run python examples/e7_env_config_scenario.py`

---

## 1. Diagram Ideas (for the tutor to draw/present live)

**Diagram A — The Request/Response Round Trip**
Client → FastAPI route → Pydantic model (validates request body) →
your function → return value → Pydantic model (serializes response) →
Client. Draw this once, plainly, before touching the watchlist code —
every `@app.get`/`@app.post` in `main.py` is an instance of this same
loop. Point at `Movie(BaseModel)` and show it appears on *both* sides of
the arrow (validates incoming, shapes outgoing).

**Diagram B — Where Pydantic Sits**
A box labeled "Untrusted JSON from the internet" → an arrow through a
box labeled "Pydantic model (the bouncer)" → a box labeled "Trusted
Python object your code can rely on." Use this to explain *why* a
`BaseModel` exists at all — it's not boilerplate, it's the only thing
standing between your function and arbitrary user input.

**Diagram C — The Event Loop vs. Thread Pool split**
Two lanes side by side: "Main thread — Event Loop" (where every `async
def` endpoint runs) and "Worker Thread Pool" (where every plain `def`
endpoint runs). Draw `time.sleep(5)` as a boulder dropped into the event
loop lane (blocks everything) vs. the same boulder dropped into a thread
pool lane (blocks only that one lane). This is the single most important
picture for explaining `examples/e4_async_sync.py`'s three endpoints —
draw it *before* running the curl-two-terminals demo, then have students
compare their drawing to what they actually observe.

**Diagram D — CRUD ↔ HTTP verb mapping**
A simple 4-row table drawn as a diagram, not prose: `GET` = Read,
`POST` = Create, `PUT` = Update, `DELETE` = Delete — each row pointing at
the matching function in `main.py` (`get_movies`, `add_movie`,
`update_movie`, `delete_movie`). Small, but worth drawing once rather
than just saying it.

---

## 2. Thought-Provoking Questions (ask before showing the answer)

1. "If you deleted the `Movie(BaseModel)` class entirely and just used a
   plain `dict` for the request body, what's the *worst* input a client
   could send that would currently be rejected but would then be
   silently accepted?"
2. "In `main.py`, `watchlist: List[Movie] = []` lives in memory. What
   happens to every movie you've added the moment the server restarts —
   and why does that same question matter enormously more once this
   becomes a real deployed service instead of a laptop demo?"
3. Look at endpoint `/1` vs `/2` in `e4_async_sync.py` — both are declared
   `async def`. "If `async def` alone made code non-blocking, why does
   `/1` still block every other request for 5 seconds? What is `async`
   actually a promise *about*?"
4. "`update_movie` and `delete_movie` both loop over `watchlist` with
   `enumerate`. At what number of movies does this stop being 'fine' in
   practice? What would you reach for instead, and why doesn't that
   change anything about the API's *behavior* from the client's point of
   view?"
5. "FastAPI runs plain `def` endpoints in a thread pool automatically.
   Given that, is there ever a *correctness* reason to still choose
   `async def` for blocking work — or is it purely a performance
   choice?" (Push students to justify with the diagram, not a guess.)

---

## 3. Live Scenarios — Pydantic only

Run standalone, no server: `uv run python examples/e5_pydantic_scenarios.py`

1. **The silently wrong type** — a `Movie(id="5", ...)` (string, not int)
   shows Pydantic *coercing* it. Compare against `id="5abc"`, which
   fails.
2. **Missing vs. extra field** — omitting a required field vs. sending
   an unrecognized extra field are handled *differently* by default.
3. **`strict` vs. default coercion** — the same `"5"` input, once with a
   normal model and once with `model_config = ConfigDict(strict=True)`.
4. **Nested model validation** — a field that's itself a `BaseModel`
   (a `Director`'s `Contact` info) shows validation errors report the
   *full path* to the bad field, not just the top-level one.

## 4. Live Scenarios — FastAPI (run the server, hit real endpoints)

Run: `uv run uvicorn examples.e6_fastapi_bug_scenarios:app --reload`
Then use `/docs` or `curl` to demo each one live.

1. **The silently wrong type, over HTTP** — same as Pydantic Scenario 1,
   but now through a real `POST` — show the 422 response body's shape
   when it *does* fail, since that's what a frontend dev actually sees.
2. **The bug hiding in plain sight** — `PUT /movies/{movie_id}`
   intentionally contains the exact `main.py` bug
   (`watchlist[index] = update_movie` instead of `updated_movie`).
   Validation passes; the *logic* is still wrong. Good lesson on what
   Pydantic can't do for you.
3. **Missing vs. extra field, over HTTP** — POST twice: once omitting
   `genre`, once adding an unexpected `rating` field. Compare status
   codes and response bodies side by side.
4. **The blocking endpoint in a crowd** — reuses `/1` from
   `e4_async_sync.py`'s pattern; open 2+ terminals, `curl` it
   concurrently, watch the server's printed order.

Each scenario file has inline docstrings with the **predict → reproduce →
lesson** structure — read the comment above each function/endpoint
before running it, make a prediction, then run it.

## 5. Live Scenario — Pydantic vs. manual `.env` config

Ties Pydantic directly back to Day 1's environment/config module. Copy
`examples/e7_env_config_scenario.env.example` to `.env` in this folder,
then run `uv run python examples/e7_env_config_scenario.py`.

1. Run once with a correct `.env` — both a hand-written
   `if os.environ.get(...)` block and a `pydantic-settings` class load
   the same 5 fields successfully. Looks like a wash.
2. Set `PORT` to a non-numeric string. Re-run — compare the two error
   messages: one is a generic Python `ValueError` that never mentions
   `PORT`/`.env`/config at all; the other names the exact field.
3. The key moment: make the manual code add a "helpful" silent default
   for a missing field, then delete that field from `.env`. The manual
   version now runs "successfully" with a silently wrong value. The
   Pydantic version still refuses to start.
4. Ask the room: which failure mode would you want at 2am during an
   incident — a crash that names the field, or a silent wrong value?

---

## Where to go next

Once these land: revisit `/2` and `/3` in `e4_async_sync.py` and have
students predict/verify the *good* patterns the same way they just broke
the bad one — comparing all three side by side is more instructive than
teaching the good pattern in isolation.
