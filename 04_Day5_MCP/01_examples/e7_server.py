"""
Scenario 7 — The smallest useful ServiceNow MCP server.

One file, one tool: create_incident. No config class, no Pydantic models,
no FastAPI. Credentials are read with os.environ; load_dotenv() fills them
from a .env file next to this script (real env vars still take priority).

Run (stdio — a Host or the MCP Inspector starts it for you), from 04_Day5_MCP/:
    1. copy .env.example to .env (same folder) and fill in your values
    2. uv run python e7_servicenow_minimal/server.py

Test with the MCP Inspector:
    npx @modelcontextprotocol/inspector uv run python e7_servicenow_minimal/server.py

PREDICT FIRST: the tool takes plain typed arguments, not a Pydantic model.
What does the Host (and the LLM) see as the tool's input schema? Open the
Inspector's "Tools" tab and compare with e2, where a Pydantic model was used.

Important for stdio servers: NEVER print() to stdout. stdout is the MCP
wire. A stray print corrupts the protocol and the Host disconnects. Use
stderr (print(..., file=sys.stderr)) if you need debug output.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

# Looks for .env next to this file, so it works from any launch directory.
# Variables already set in the environment (e.g. by a Host's "env" block) win.
load_dotenv(Path(__file__).parent / ".env")

mcp = MCPServer("servicenow-minimal")


def _instance_url() -> str:
    # Only adds https:// if the scheme is missing. Use the full host, e.g.
    # "dev12345.service-now.com" — a bare "dev12345" is not expanded for you.
    url = os.environ["SERVICENOW_INSTANCE"].strip().rstrip("/")
    return url if url.startswith(("http://", "https://")) else f"https://{url}"


@mcp.tool(
    name="create_incident",
    description=(
        "Create a ServiceNow incident. Use when the user asks to open, raise or "
        "log an incident/ticket. Convert their message into a short title and a "
        "detailed description first."
    ),
)
async def create_incident(
    short_description: str,
    description: str,
    urgency: Literal["1", "2", "3"] = "2",
    impact: Literal["1", "2", "3"] = "2",
) -> dict[str, Any]:
    """urgency / impact: 1 = high, 2 = medium, 3 = low."""
    base = _instance_url()
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{base}/api/now/table/incident",
            auth=(os.environ["SERVICENOW_USERNAME"], os.environ["SERVICENOW_PASSWORD"]),
            headers={"Accept": "application/json"},
            json={
                "short_description": short_description,
                "description": description,
                "urgency": urgency,
                "impact": impact,
            },
        )
    if response.is_error:
        # Only ToolError text reaches the LLM. Any other exception is shown as a bare
        # "Error executing tool ...", which hides things like a 401 from the model.
        raise ToolError(f"ServiceNow returned {response.status_code}: {response.text[:300]}")
    result = response.json()["result"]
    return {
        "number": result.get("number"),
        "sys_id": result["sys_id"],
        "url": f"{base}/nav_to.do?uri=incident.do?sys_id={result['sys_id']}",
    }


if __name__ == "__main__":
    mcp.run()  # stdio
