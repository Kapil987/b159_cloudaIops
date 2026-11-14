from __future__ import annotations

import httpx

from config import Settings
from models import IncidentDraft, IncidentResult, IncidentSolution, IncidentSolutionsResult


class ServiceNowClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = f"{settings.servicenow_instance}/api/now/table"
        self._auth = (
            settings.servicenow_username,
            settings.servicenow_password.get_secret_value(),
        )

    async def create_incident(self, draft: IncidentDraft) -> IncidentResult:
        url = f"{self._base_url}/incident"
        try:
            async with httpx.AsyncClient(timeout=self._settings.servicenow_timeout_seconds) as client:
                response = await client.post(
                    url,
                    auth=self._auth,
                    headers={"Accept": "application/json", "Content-Type": "application/json"},
                    json=draft.to_servicenow_payload(),
                )
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Could not reach ServiceNow. Check SERVICENOW_INSTANCE in .env and confirm this machine "
                f"can access {self._settings.servicenow_instance}. Network error: {exc}"
            ) from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise RuntimeError(f"ServiceNow incident creation failed: {detail}") from exc

        result = response.json().get("result", {})
        sys_id = result.get("sys_id")
        if not sys_id:
            raise RuntimeError(f"ServiceNow response did not include a sys_id: {response.text}")

        incident_url = f"{self._settings.servicenow_instance}/nav_to.do?uri=incident.do?sys_id={sys_id}"
        return IncidentResult(
            number=result.get("number"),
            sys_id=sys_id,
            state=result.get("state"),
            short_description=result.get("short_description"),
            url=incident_url,
            raw=result,
        )

    async def get_recent_incident_solutions(self, limit: int = 5) -> IncidentSolutionsResult:
        url = f"{self._base_url}/incident"
        safe_limit = max(1, min(limit, 20))
        params = {
            "sysparm_query": "close_notesISNOTEMPTY^ORDERBYDESCclosed_at^ORDERBYDESCsys_updated_on",
            "sysparm_fields": "number,sys_id,short_description,description,close_notes,closed_at,state",
            "sysparm_display_value": "true",
            "sysparm_limit": safe_limit,
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.servicenow_timeout_seconds) as client:
                response = await client.get(
                    url,
                    auth=self._auth,
                    headers={"Accept": "application/json"},
                    params=params,
                )
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Could not reach ServiceNow. Check SERVICENOW_INSTANCE in .env and confirm this machine "
                f"can access {self._settings.servicenow_instance}. Network error: {exc}"
            ) from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise RuntimeError(f"ServiceNow incident solution lookup failed: {detail}") from exc

        incidents = [
            IncidentSolution(
                number=item.get("number"),
                sys_id=item.get("sys_id"),
                short_description=item.get("short_description"),
                description=item.get("description"),
                close_notes=item.get("close_notes"),
                closed_at=item.get("closed_at"),
                state=item.get("state"),
            )
            for item in response.json().get("result", [])
        ]
        return IncidentSolutionsResult(count=len(incidents), incidents=incidents)

    async def search_incident_solutions(self, query: str, limit: int = 5) -> IncidentSolutionsResult:
        url = f"{self._base_url}/incident"
        safe_query = query.strip()
        if not safe_query:
            return await self.get_recent_incident_solutions(limit=limit)

        safe_limit = max(1, min(limit, 20))
        params = {
            "sysparm_query": "close_notesISNOTEMPTY^ORDERBYDESCclosed_at^ORDERBYDESCsys_updated_on",
            "sysparm_fields": "number,sys_id,short_description,description,close_notes,closed_at,state",
            "sysparm_display_value": "true",
            "sysparm_limit": 100,
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.servicenow_timeout_seconds) as client:
                response = await client.get(
                    url,
                    auth=self._auth,
                    headers={"Accept": "application/json"},
                    params=params,
                )
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Could not reach ServiceNow. Check SERVICENOW_INSTANCE in .env and confirm this machine "
                f"can access {self._settings.servicenow_instance}. Network error: {exc}"
            ) from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise RuntimeError(f"ServiceNow incident solution search failed: {detail}") from exc

        query_terms = {
            term.lower()
            for term in safe_query.replace(":", " ").replace("/", " ").replace("-", " ").split()
            if len(term) > 2
        }
        if not query_terms:
            query_terms = {safe_query.lower()}

        scored_incidents: list[tuple[int, IncidentSolution]] = []
        for item in response.json().get("result", []):
            searchable_text = " ".join(
                str(item.get(field) or "")
                for field in ("short_description", "description", "close_notes")
            ).lower()
            score = sum(1 for term in query_terms if term in searchable_text)
            if score == 0:
                continue

            scored_incidents.append(
                (
                    score,
                    IncidentSolution(
                        number=item.get("number"),
                        sys_id=item.get("sys_id"),
                        short_description=item.get("short_description"),
                        description=item.get("description"),
                        close_notes=item.get("close_notes"),
                        closed_at=item.get("closed_at"),
                        state=item.get("state"),
                    ),
                )
            )

        incidents = [
            incident
            for _, incident in sorted(
                scored_incidents,
                key=lambda scored_incident: scored_incident[0],
                reverse=True,
            )[:safe_limit]
        ]

        return IncidentSolutionsResult(count=len(incidents), incidents=incidents)
