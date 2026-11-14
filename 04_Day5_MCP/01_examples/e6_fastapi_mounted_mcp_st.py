"""
Scenario 6 — Mount an MCP server inside FastAPI (closing the loop to
26_service_now/fastapi_app.py).

Run:
    uv run uvicorn e6_fastapi_mounted_mcp:app --reload

Then:
    GET  http://127.0.0.1:8000/health   <- plain REST, curl-able normally
    POST http://127.0.0.1:8000/mcp      <- MCP protocol endpoint, NOT a
                                            normal REST endpoint

PREDICT FIRST: once mounted, is /mcp a normal REST endpoint you could
curl and get plain JSON back from directly? Try curling it with a random
body and see what actually comes back — it speaks the MCP transport
protocol (streamable-http), not arbitrary REST. A real MCP Host's client
library knows how to speak this; a naive curl does not, and you'll see
a protocol-shaped error/response rather than "404 not found" or a normal
JSON payload — which is itself the lesson: mounting an MCP server next
to REST endpoints in the same FastAPI app does not make the MCP endpoint
"just another REST route."

This is the exact structure 26_service_now/fastapi_app.py uses:
mcp.streamable_http_app() + a lifespan that runs mcp.session_manager +
app.mount("/", mcp_asgi_app) LAST, after all plain REST routes are
registered.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from mcp.server.mcpserver import MCPServer

# --- Same structured tool from Scenario 2, condensed ------------------


class TicketDraft(BaseModel):
    title: str = Field(..., min_length=5) # or we can say this as short description in service now terms
    description: str = Field(..., min_length=10)
    priority: str = Field("medium")


mcp = MCPServer("e6-fastapi-mounted-server")


@mcp.tool(name="create_ticket", description="Create a support ticket.", structured_output=True)
def create_ticket(draft: TicketDraft) -> dict[str, Any]:
    return {"ticket_id": "TICKET-0001", "title": draft.title, "priority": draft.priority}


# --- FastAPI app ----------

mcp_asgi_app = mcp.streamable_http_app(
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI lifespan started")
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Day 4 — MCP mounted in FastAPI", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mcp_endpoint": "/mcp"}


# Mount LAST — plain REST routes above are matched first; everything
# else falls through to the MCP ASGI app.
app.mount("/", mcp_asgi_app)
