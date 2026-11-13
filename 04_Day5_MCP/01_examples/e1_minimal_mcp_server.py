"""
Scenario 1 — The smallest possible MCP server.

Run:
    uv run python examples/e1_minimal_mcp_server.py

PREDICT FIRST: what happens when you run this? It's not a normal script
— there's no print statement that runs and exits. MCPServer's default
transport is "stdio": the process starts and then WAITS, listening for
an MCP Host to connect to it over stdin/stdout. You won't see obvious
output because nothing has connected yet. Press Ctrl+C to stop it.

This is the single biggest surprise for people new to MCP: an MCP server
is a long-running service waiting for a Host, not a CLI tool that runs
once and prints a result.
"""
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("day4-minimal-server")


@mcp.tool(
    name="add_numbers",
    description="Add two numbers together and return the sum.",
)
def add_numbers(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    mcp.run()  # default transport="stdio"
