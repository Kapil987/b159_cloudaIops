"""
v3: the v2 graph behind a FastAPI server, with a plain HTML/CSS/JS page on top.

Run from the project root:
    uv run uvicorn v3_fastapi_ui.main:app --port 8000
then open http://localhost:8000

Nothing about the agents changes. This file imports the SAME graph that v2 uses
(v2_rag_plus_postgres/graph.py) and only adds a web layer around it:

    browser  --POST /api/ask/stream-->  FastAPI  --graph.astream()-->  router -> agents -> merge
       ^                                   |
       +------ server-sent events ---------+   (one event per finished step)

Things worth noticing:
- client_id is read from the SERVER-SIDE session (a signed cookie), never from the
  request body. A browser can send any JSON it likes, so anything in the body is untrusted.
- The graph nodes are plain functions (boto3 and psycopg are not async). LangGraph
  runs them in worker threads when we call astream/ainvoke, so the event loop stays
  free and one slow question does not block other users.
"""
import json
import logging
import secrets
import sys
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# v2's graph.py does `from db import TOOLS`, so v2's folder must be on the path too.
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v2_rag_plus_postgres"))

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.sessions import SessionMiddleware

from common.config import AS_OF_DATE, SESSION_SECRET
from common.users import FAKE_USERS
from graph import graph  # type: ignore[import-not-found]  # v2's graph, unchanged. Found via the sys.path line above.

log = logging.getLogger("contract_assistant")
STATIC_DIR = Path(__file__).resolve().parent / "static"

if not SESSION_SECRET:
    log.warning("SESSION_SECRET is not set. Using a random one, so everyone is logged out on restart.")

app = FastAPI(title="Contract Assistant v3", docs_url="/docs")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET or secrets.token_hex(32),
    session_cookie="lf_session",
    max_age=8 * 60 * 60,   # a working day
    same_site="lax",       # the cookie is not sent on cross-site POSTs
    https_only=False,      # set True once the app is served over HTTPS
)


# --- who is logged in ----------------------------------------------------------------

def current_user(request: Request) -> dict[str, str]:
    """The logged-in attorney, read from the signed session cookie. 401 if nobody is."""
    username = request.session.get("username")
    user = FAKE_USERS.get(username) if isinstance(username, str) else None
    if user is None:
        raise HTTPException(status_code=401, detail="Please log in.")
    return {"username": username, **user}  # type: ignore[arg-type]


class LoginBody(BaseModel):
    username: str


class AskBody(BaseModel):
    # Only the question. There is deliberately no client_id field: it comes from the session.
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=1000)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/users")
async def users() -> list[dict[str, str]]:
    """The mock login choices. A real system would show a sign-in form instead."""
    return [{"username": u, "name": v["name"], "client_id": v["client_id"]} for u, v in FAKE_USERS.items()]


@app.post("/api/login")
async def login(body: LoginBody, request: Request) -> dict[str, str]:
    user = FAKE_USERS.get(body.username)
    if user is None:
        raise HTTPException(status_code=404, detail="Unknown attorney.")
    request.session.clear()  # start from a clean session
    request.session["username"] = body.username
    return {"username": body.username, **user}


@app.post("/api/logout")
async def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"status": "logged out"}


@app.get("/api/me")
async def me(request: Request) -> dict[str, Any]:
    """Who is logged in? Answers 200 with user=null when nobody is, so a fresh page
    load is not logged as an error. The endpoints that need a login return 401."""
    try:
        user = current_user(request)
    except HTTPException:
        user = None
    return {"user": user, "as_of_date": AS_OF_DATE.isoformat()}


# --- asking questions ----------------------------------------------------------------

TRACE_KEYS = ("route", "tool_call", "contracts", "passages")


@app.post("/api/ask")
async def ask(body: AskBody, user: dict[str, str] = Depends(current_user)) -> dict[str, Any]:
    """One request, one answer. Waits for the whole graph, like v1 and v2 did."""
    result = await graph.ainvoke({"question": body.question, "client_id": user["client_id"]})
    return jsonable_encoder({"answer": result["answer"], **{k: result.get(k) for k in TRACE_KEYS}})


def _sse(event: str, data: dict[str, Any]) -> str:
    """Format one server-sent event: an event name, a JSON line, and a blank line."""
    return f"event: {event}\ndata: {json.dumps(jsonable_encoder(data))}\n\n"


async def _stream(question: str, client_id: str) -> AsyncIterator[str]:
    """Run the graph and send one event as each step finishes.

    stream_mode="updates" yields {node_name: what_that_node_returned} each time a
    node completes, so the page can show Router -> Postgres -> Knowledge Base -> Answer live.
    """
    started = last = time.perf_counter()
    try:
        async for update in graph.astream({"question": question, "client_id": client_id}, stream_mode="updates"):
            for node, data in update.items():
                now = time.perf_counter()
                yield _sse("step", {"node": node, "ms": round((now - last) * 1000), "data": data or {}})
                last = now
        yield _sse("done", {"ms": round((time.perf_counter() - started) * 1000)})
    except Exception as exc:  # setup problems (AWS, Postgres) are shown plainly in the page
        log.exception("question failed")
        yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"})


@app.post("/api/ask/stream")
async def ask_stream(body: AskBody, user: dict[str, str] = Depends(current_user)) -> StreamingResponse:
    return StreamingResponse(
        _stream(body.question, user["client_id"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --- the page ------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
