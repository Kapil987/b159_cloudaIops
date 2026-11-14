"""
Scenario 8 — ServiceNow MCP server, "a little more" than e7.

Two tools only: create_incident and get_incident.

Same building blocks as 26_service_now_project, split into small files:

    config.py             Settings (pydantic-settings, .env, SecretStr)
    models.py             tool input/output models
    servicenow_client.py  ServiceNow Table API calls (no MCP code)
    server.py             this file: the MCP server + tools

Transport: streamable-http. This server is a long-running process you start
yourself; Hosts connect to it at http://127.0.0.1:8000/mcp (see MCP_HOST / MCP_PORT).

Run, from 04_Day5_MCP/:
    1. copy .env.example to .env (same folder) and fill in your values
    2. uv run python e8_servicenow_with_settings/server.py     (leave it running)

Test with the MCP Inspector (second terminal):
    npx @modelcontextprotocol/inspector
    then choose "Streamable HTTP" and URL http://127.0.0.1:8000/mcp

PREDICT FIRST: delete the .env / env vars and start the server. When does it
fail — at startup, or only when you call a tool? (Look at where `Settings()`
is created in config.py.) Failing at startup is deliberate: "server failed to
start: SERVICENOW_PASSWORD field required" is easier to debug than a tool that
errors on every call.

There is NO login on this endpoint. Anyone who can reach the port can create
incidents with the credentials in your .env. Keep MCP_HOST on 127.0.0.1 unless
you put authentication in front of it.
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from config import settings
from models import IncidentDetails, IncidentDraft, IncidentResult
from servicenow_client import ServiceNowClient, ServiceNowError

servicenow = ServiceNowClient(settings)

mcp = MCPServer(
    "servicenow-with-settings",
    instructions=(
        "Two tools. Use get_incident to look up one incident by its number (like INC0010001) and "
        "read its status or close notes. Use create_incident when the user asks to open a new "
        "incident; turn natural language into the IncidentDraft fields first."
    ),
)


@mcp.tool(
    name="create_incident",
    description="Create a ServiceNow incident from a structured draft (title, description, urgency, impact, ...).",
    structured_output=True,
)
async def create_incident(draft: IncidentDraft) -> IncidentResult:
    try:
        return await servicenow.create_incident(draft)
    except ServiceNowError as exc:
        raise ToolError(str(exc)) from exc  # ToolError text reaches the LLM; other exceptions are hidden


@mcp.tool(
    name="get_incident",
    description=(
        "Look up one ServiceNow incident by its number, e.g. INC0010001. Returns title, description, "
        "state, urgency, opened date, close notes (if closed) and a link."
    ),
    structured_output=True,
)
async def get_incident(number: str) -> IncidentDetails:
    try:
        return await servicenow.get_incident(number)
    except ServiceNowError as exc:
        raise ToolError(str(exc)) from exc


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=settings.mcp_host,
        port=settings.mcp_port,
        streamable_http_path="/mcp",
    )
