from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class BrainQueryRequest(BaseModel):
    aura_id: str = Field(..., min_length=1, max_length=128)
    brain_id: str = Field(..., min_length=1, max_length=128)
    query: str = Field(..., min_length=1, max_length=4000)
    context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("context")
    @classmethod
    def validate_context(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("context must be an object")
        if value.get("aura_id") and value["aura_id"] != value.get("aura_id"):
            return value
        return value


class BrainQueryResponse(BaseModel):
    aura_id: str
    brain_id: str
    response: str
    model: str = "Qwen3.5-4B"
    request_id: str | None = None
    status: str = "ok"


class HealthResponse(BaseModel):
    status: str
    model: str
    version: str = "1.0.0"


class ReadyResponse(BaseModel):
    status: str
    model_loaded: bool
    model: str
