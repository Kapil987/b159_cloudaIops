from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from models import Capability, IncidentDraft, IncidentResult, IncidentSolutionsResult, RuntimeConfig
from servicenow_fastmcp import discover_capabilities, get_loaded_runtime_config, mcp, servicenow


mcp_asgi_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="ServiceNow FastMCP Server",
    description="FastAPI-hosted FastMCP server for Azure agents to discover and create ServiceNow incidents.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mcp_endpoint": "/mcp"}


@app.get("/capabilities", response_model=Capability)
async def http_capabilities() -> Capability:
    return discover_capabilities()


@app.get("/runtime-config", response_model=RuntimeConfig)
async def runtime_config() -> RuntimeConfig:
    return get_loaded_runtime_config()


@app.post("/incidents", response_model=IncidentResult)
async def http_create_incident(draft: IncidentDraft) -> IncidentResult:
    try:
        return await servicenow.create_incident(draft)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/incident-solutions", response_model=IncidentSolutionsResult)
async def http_recent_incident_solutions(limit: int = 5) -> IncidentSolutionsResult:
    try:
        return await servicenow.get_recent_incident_solutions(limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/incident-solutions/search", response_model=IncidentSolutionsResult)
async def http_search_incident_solutions(query: str, limit: int = 5) -> IncidentSolutionsResult:
    try:
        return await servicenow.search_incident_solutions(query=query, limit=limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


app.mount("/", mcp_asgi_app)
