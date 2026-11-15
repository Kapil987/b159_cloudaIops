"""
Scenario 3 — A resource vs. a tool that returns the same data.

Run:
    uv run python examples/e3_resource_vs_tool.py

Mirrors 26_service_now/servicenow_fastmcp.py's `incident_schema`
resource (servicenow://incident/schema) — here implemented twice: once
correctly as a @mcp.resource, and once (deliberately, for contrast) as a
@mcp.tool that returns the exact same JSON.

PREDICT FIRST: could a Host get the same JSON out of both? (Yes.) So
what's actually different? Resources are meant to be READ, not
"decided whether to call" — a Host can list and attach resources to
context proactively (e.g. "always give the model this schema"), while a
tool only runs when the model explicitly decides to invoke it. Functionally
similar output; conceptually different role in the protocol.
"""
from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from app_logging.shared_logging_config import setup_logging

logger = setup_logging(__name__) 
mcp = MCPServer("day4-resource-vs-tool-server")

_TICKET_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 5},
        "description": {"type": "string", "minLength": 10},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
    },
    "required": ["title", "description"],
}


# The RIGHT way: a resource. No side effects, just data, addressed by a
# URI. A Host can fetch this proactively without any model "decision."
# A URL is a type of URI, but not every URI is a URL, file:///home/user/data.json	File URI
# Resource tells the AI additional information it may need to make a good decision.
@mcp.resource(
    "tickets://schema", # URI (Uniform Resource Identifier)
    name="ticket_schema",
    description="JSON schema for the structured ticket payload agents should produce before calling create_ticket.",
    mime_type="application/json",
)
def ticket_schema_resource() -> dict[str, Any]:
    logger.debug(f"ticket schema resource {_TICKET_SCHEMA}",)
    return _TICKET_SCHEMA


# The CONTRAST: the same data, exposed as a tool instead. Works, but the
# model now has to actively decide to "call a tool" just to read static
# data that never changes — that's the wrong mental model for this kind
# of information, even though the output is identical.
# Tool schema tells the AI how to call a tool.
@mcp.tool(
    name="get_ticket_schema",
    description="Return the JSON schema for a ticket payload.",
    structured_output=True,
)
def get_ticket_schema_tool() -> dict[str, Any]:
    logger.debug(f"ticket schema{_TICKET_SCHEMA}",)
    return _TICKET_SCHEMA


if __name__ == "__main__":
    logger.info("Starting MCP server")
    mcp.run()
