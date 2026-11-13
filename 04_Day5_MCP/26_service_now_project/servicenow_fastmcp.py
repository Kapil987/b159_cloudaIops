from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from config import settings
from models import Capability, IncidentDraft, IncidentResult, IncidentSolutionsResult, RuntimeConfig
from servicenow_client import ServiceNowClient


servicenow = ServiceNowClient(settings)


mcp = FastMCP(
    "servicenow-incident-mcp",
    instructions=(
        "Discover this server's tools, then use create_incident when a user asks "
        "to open a ServiceNow incident. Convert natural language into the required "
        "IncidentDraft fields before calling the tool."
    ),
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
)


@mcp.tool(
    name="discover_capabilities",
    description="Describe the ServiceNow operations exposed by this MCP server.",
    structured_output=True,
)
def discover_capabilities() -> Capability:
    return Capability(
        name="servicenow_incident_creation",
        description=(
            "Create ServiceNow incidents and retrieve recent closed incident close notes "
            "for solution suggestions."
        ),
        required_fields=["short_description", "description"],
        optional_fields=[
            "urgency",
            "impact",
            "caller_id",
            "category",
            "subcategory",
            "assignment_group",
            "contact_type",
            "business_service",
            "cmdb_ci",
            "additional_fields",
        ],
        mcp_endpoint="/mcp",
    )


def get_loaded_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        servicenow_instance=settings.servicenow_instance,
        servicenow_username=settings.servicenow_username,
        servicenow_password_configured=bool(settings.servicenow_password.get_secret_value()),
        servicenow_timeout_seconds=settings.servicenow_timeout_seconds,
    )


@mcp.tool(
    name="get_runtime_config",
    description="Show the non-secret ServiceNow configuration loaded by this running MCP server.",
    structured_output=True,
)
def get_runtime_config() -> RuntimeConfig:
    return get_loaded_runtime_config()


@mcp.tool(
    name="create_incident",
    description=(
        "Create a ServiceNow incident. Use this after extracting a title, detailed "
        "description, urgency, impact, caller, category, and any routing hints from the user prompt."
    ),
    structured_output=True,
)
async def create_incident(draft: IncidentDraft) -> IncidentResult:
    return await servicenow.create_incident(draft)


@mcp.tool(
    name="get_recent_incident_solutions",
    description=(
        "Return the most recent ServiceNow incidents that have close notes. "
        "Use this before creating a new incident to suggest prior resolutions to the user."
    ),
    structured_output=True,
)
async def get_recent_incident_solutions(limit: int = 5) -> IncidentSolutionsResult:
    return await servicenow.get_recent_incident_solutions(limit=limit)


@mcp.tool(
    name="search_incident_solutions",
    description=(
        "Search ServiceNow incidents with close notes by a topic or error phrase. "
        "Use this before creating a new incident to find prior resolutions related to the user's issue."
    ),
    structured_output=True,
)
async def search_incident_solutions(query: str, limit: int = 5) -> IncidentSolutionsResult:
    return await servicenow.search_incident_solutions(query=query, limit=limit)


@mcp.resource(
    "servicenow://incident/schema",
    name="incident_schema",
    description="JSON schema for the structured incident payload agents should produce before calling create_incident.",
    mime_type="application/json",
)
def incident_schema() -> dict[str, Any]:
    return IncidentDraft.model_json_schema()


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
