"""Talks to the ServiceNow Table API. No MCP code in here."""
from __future__ import annotations

import re
from typing import Any

import httpx

from config import Settings
from models import IncidentDetails, IncidentDraft, IncidentResult


class ServiceNowError(RuntimeError): # RuntimeError is a built-in Python exception class. You don't need to import it from anywhere.
    """An expected failure (bad credentials, unreachable host, bad or unknown incident number). server.py shows it to the LLM."""


class ServiceNowClient:
    def __init__(self, cfg: Settings) -> None:
        self._cfg = cfg
        self._table = f"{cfg.servicenow_instance}/api/now/table/incident" # https://dev443316.service-now.com/api/now/table/incident
        self._auth = (cfg.servicenow_username, cfg.servicenow_password.get_secret_value()) # You need .get_secret_value() because Pydantic's SecretStr does not return the actual password

    def _incident_url(self, sys_id: str) -> str:
        return f"{self._cfg.servicenow_instance}/nav_to.do?uri=incident.do?sys_id={sys_id}"

    async def _request(self, method: str, **kwargs: Any) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self._cfg.servicenow_timeout_seconds) as client:
                response = await client.request(
                    method, self._table, auth=self._auth, headers={"Accept": "application/json"}, **kwargs
                )
        except httpx.RequestError as exc:
            raise ServiceNowError(f"Could not reach {self._cfg.servicenow_instance}: {exc}") from exc
        if response.is_error:
            raise ServiceNowError(f"ServiceNow returned {response.status_code}: {response.text[:500]}")
        return response.json()

    async def create_incident(self, draft: IncidentDraft) -> IncidentResult:
        payload = draft.model_dump(exclude_none=True)
        result = (await self._request("POST", json=payload))["result"]
        sys_id = result["sys_id"]
        return IncidentResult(
            number=result.get("number"),
            sys_id=sys_id,
            state=result.get("state"),
            url=self._incident_url(sys_id), # sys_id
        )

    async def get_incident(self, number: str) -> IncidentDetails:
        number = number.strip().upper()
        if not re.fullmatch(r"INC\d+", number): # INC0010016
            raise ServiceNowError(f"'{number}' is not an incident number. Expected something like INC0010001.")
        params = {
            "number": number,  # plain field filter, no query language needed
            "sysparm_fields": "number,sys_id,short_description,description,state,urgency,opened_at,close_notes",
            "sysparm_display_value": "true",  # "In Progress" instead of "2"
            "sysparm_limit": 1,
        }
        rows = (await self._request("GET", params=params))["result"]
        if not rows:
            raise ServiceNowError(f"No incident found with number {number}.")
        row = rows[0]
        return IncidentDetails(
            number=row["number"],
            short_description=row.get("short_description"),
            description=row.get("description"),
            state=row.get("state"),
            urgency=row.get("urgency"),
            opened_at=row.get("opened_at"),
            close_notes=row.get("close_notes") or None,
            url=self._incident_url(row["sys_id"]),
        )
