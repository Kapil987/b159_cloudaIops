"""
Scenario 4 — A prompt template (the primitive 26_service_now doesn't use yet).

Run:
    uv run python examples/e4_prompt_template.py

PREDICT FIRST: a prompt template doesn't call any API or touch any data
— so what is it actually for, if not "doing" something?

Answer: a Prompt is a reusable, parameterized MESSAGE a Host can offer to
its user as a menu item (e.g. a "/" slash-command in a chat UI) or hand
to the model directly. It standardizes a common REQUEST shape, the same
way create_incident standardizes a common ACTION shape. Here: turn "user
complains about X" into a consistent instruction asking the model to
draft a ticket.
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("day4-prompt-server")


@mcp.prompt(
    name="draft_ticket_from_complaint",
    description="Turn a user's raw complaint into an instruction asking the model to draft a structured support ticket.",
)
def draft_ticket_from_complaint(complaint: str) -> str:
    return (
        "A user reported the following issue:\n\n"
        f'"{complaint}"\n\n'
        "Draft a support ticket for this. Produce a concise title, a "
        "detailed description including any symptoms and impact you can "
        "infer, and a priority (low/medium/high) based on how severe "
        "this sounds. Use the create_ticket tool's schema."
    )


if __name__ == "__main__":
    # No Host needed to see what this produces — the prompt function is
    # just a plain function until an MCP Host calls it through the
    # protocol.
    example = draft_ticket_from_complaint(
        complaint="I can't log into the payroll portal, it's been down since this morning."
    )
    print("Prompt template output (this is the string a Host would send to the model):\n")
    print(example)

    mcp.run()
