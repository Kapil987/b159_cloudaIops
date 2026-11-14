"""Pydantic models: tool inputs and outputs."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class IncidentDraft(BaseModel):
    short_description: str = Field(..., min_length=5, max_length=160, description="Concise incident title.")
    description: str = Field(..., min_length=10, description="Symptoms, impact, and what was already tried.")
    urgency: Literal["1", "2", "3"] = Field("2", description="1=high, 2=medium, 3=low.")
    impact: Literal["1", "2", "3"] = Field("2", description="1=high, 2=medium, 3=low.")
    category: str | None = Field(None, description="e.g. software, hardware, network.")
    caller_id: str | None = Field(None, description="Caller sys_id, user name or email, if known.")


class IncidentResult(BaseModel):
    number: str | None = None
    sys_id: str
    state: str | None = None
    url: str


class IncidentDetails(BaseModel):
    number: str
    short_description: str | None = None
    description: str | None = None
    state: str | None = None
    urgency: str | None = None
    opened_at: str | None = None
    close_notes: str | None = None
    url: str
