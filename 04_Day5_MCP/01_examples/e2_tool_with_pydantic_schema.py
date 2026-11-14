"""
Scenario 2 — Tools with structured input/output (the ServiceNow pattern).

Run:
    uv run python examples/e2_tool_with_pydantic_schema.py

Mirrors 26_service_now/servicenow_fastmcp.py's create_incident tool,
stripped down to a fake "support ticket" domain with no real API calls.
Same idea: define a Pydantic model for the tool's input, and the MCP
Host/model gets a real typed JSON schema to fill in — not just "a
string" it has to format correctly by luck.

PREDICT FIRST: if a Host sends {"title": "Hi"} (missing the required
"description" field), where does the rejection happen — inside
create_ticket()'s body, or before your code even runs?
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("e2-structured-tool-server")


class TicketDraft(BaseModel):
    # title: str = Field(..., min_length=5, description="A short ticket title.")
    short_description: str = Field(..., min_length=5, description="A short ticket title.")
    description: str = Field(..., min_length=10, description="Full details of the issue.")
    priority: str = Field("medium", description="One of: low, medium, high.")


class TicketResult(BaseModel):
    ticket_id: str
    title: str
    priority: str


# In-memory "database" for this teaching example only.
_tickets: dict[str, TicketDraft] = {}


@mcp.tool(
    name="create_ticket",
    description=(
        "Create a support ticket. Extract a concise title, a detailed "
        "description, and a priority (low/medium/high) from the user's message "
        "before calling this tool."
    ),
    structured_output=True,
)
def create_ticket(draft: TicketDraft) -> TicketResult:
    ticket_id = f"TICKET-{len(_tickets) + 1:04d}" # generate ticket number as TICKET-0001
    _tickets[ticket_id] = draft
    return TicketResult(ticket_id=ticket_id, title=draft.short_description, priority=draft.priority)


if __name__ == "__main__":
    # Try this locally without a Host, just to see the schema MCPServer
    # generates from TicketDraft — this is exactly what gets sent to a
    # Host during discovery, before any tool is ever called.
    print("TicketDraft JSON schema (this is what the model sees):")
    print(TicketDraft.model_json_schema())

    mcp.run()
