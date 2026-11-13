from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class IncidentDraft(BaseModel):
    short_description: str = Field(
        ...,
        min_length=5,
        max_length=160,
        description="A concise incident title for the ServiceNow short_description field.",
    )
    description: str = Field(
        ...,
        min_length=10,
        description="Detailed issue context, symptoms, impact, and any troubleshooting already attempted.",
    )
    urgency: Literal["1", "2", "3"] = Field(
        "2",
        description="ServiceNow urgency: 1=high, 2=medium, 3=low.",
    )
    impact: Literal["1", "2", "3"] = Field(
        "2",
        description="ServiceNow impact: 1=high, 2=medium, 3=low.",
    )
    caller_id: str | None = Field(
        None,
        description="Caller sys_id, user name, email, or display value if your ServiceNow instance accepts it.",
    )
    category: str | None = Field(None, description="ServiceNow incident category, such as software, hardware, or network.")
    subcategory: str | None = Field(None, description="ServiceNow incident subcategory when known.")
    assignment_group: str | None = Field(None, description="Assignment group sys_id, name, or display value if accepted.")
    contact_type: str = Field("self-service", description="ServiceNow contact_type value.")
    business_service: str | None = Field(None, description="Affected business service sys_id, name, or display value.")
    cmdb_ci: str | None = Field(None, description="Affected configuration item sys_id, name, or display value.")
    additional_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional ServiceNow incident table fields to merge into the payload.",
    )

    @field_validator(
        "short_description",
        "description",
        "caller_id",
        "category",
        "subcategory",
        "assignment_group",
        "contact_type",
        "business_service",
        "cmdb_ci",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    def to_servicenow_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "short_description": self.short_description,
            "description": self.description,
            "urgency": self.urgency,
            "impact": self.impact,
            "contact_type": self.contact_type,
        }
        optional_fields = {
            "caller_id": self.caller_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "assignment_group": self.assignment_group,
            "business_service": self.business_service,
            "cmdb_ci": self.cmdb_ci,
        }
        payload.update({key: value for key, value in optional_fields.items() if value})
        payload.update({key: value for key, value in self.additional_fields.items() if value is not None})
        return payload


class IncidentResult(BaseModel):
    number: str | None = None
    sys_id: str
    state: str | None = None
    short_description: str | None = None
    url: HttpUrl | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class IncidentSolution(BaseModel):
    number: str | None = None
    sys_id: str | None = None
    short_description: str | None = None
    description: str | None = None
    close_notes: str | None = None
    closed_at: str | None = None
    state: str | None = None


class IncidentSolutionsResult(BaseModel):
    count: int
    incidents: list[IncidentSolution]


class Capability(BaseModel):
    name: str
    description: str
    required_fields: list[str]
    optional_fields: list[str]
    mcp_endpoint: str


class RuntimeConfig(BaseModel):
    servicenow_instance: str
    servicenow_username: str
    servicenow_password_configured: bool
    servicenow_timeout_seconds: float
