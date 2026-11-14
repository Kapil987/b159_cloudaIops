"""
Scenario 5 — Break it: the vague-description tool.

Run:
    uv run python examples/e5_break_the_description.py

PREDICT FIRST, then (if you have access to a real MCP-capable Host —
Claude Desktop, VS Code Copilot Agent mode, etc.) connect this server
and give the model an ambiguous natural-language request like "the
payroll portal login is broken for everyone, can you log this?" Watch
which of the two near-identical tools it reaches for, and how confidently
it fills in arguments for each.

Both tools do the EXACT SAME THING (create_ticket_good calls the same
logic as create_ticket_vague). The only difference is the `description`
string. This is the live version of Thought Question 1 — a tool's
description is not documentation for humans, it's the ONLY information
the model has to decide when and how to call it. Vague description in,
unreliable tool-selection out — even though the code itself has zero
bugs.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("e5-description-comparison-server")


class TicketDraft(BaseModel):
    # or we can say this as short description in service now terms
    title: str = Field(..., description="Concise ticket title.") # The ... (Ellipsis) means "This field is required; there is no default value."
    description: str = Field(..., description="Full issue details.")
    priority: str = Field("medium", description="low, medium, or high.")


def _create(draft: TicketDraft) -> dict[str, Any]:
    return {"ticket_id": "TICKET-0001", "title": draft.title, "priority": draft.priority}


# GOOD: precise, tells the model exactly what to extract and when to use it.
# (This is the real style used by create_incident in servicenow_fastmcp.py.)
@mcp.tool(
    name="create_ticket_good",
    description=(
        "Create a support ticket when a user reports a problem that needs "
        "tracking or follow-up. Extract a concise title, a detailed "
        "description of symptoms/impact, and a priority (low/medium/high — "
        "default medium if unclear) from the user's message before calling."
    ),
    structured_output=True,
)
def create_ticket_good(draft: TicketDraft) -> dict[str, Any]:
    return _create(draft)


# VAGUE: deliberately unhelpful, for contrast only.
@mcp.tool(
    name="create_ticket_vague",
    description="Does ticket stuff.",
    structured_output=True,
)
def create_ticket_vague(draft: TicketDraft) -> dict[str, Any]:
    return _create(draft)


if __name__ == "__main__":
    print("Both tools are functionally identical. Connect a real MCP Host")
    print("and compare how reliably each gets selected/filled in for the")
    print("same ambiguous user request.")
    mcp.run()
