"""Schemas for the Personal Brain API boundary."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BrainQueryRequest(BaseModel):
    """Request sent from an application to the user's Personal Brain."""

    query: str = Field(..., min_length=1, max_length=5000)
    context: dict[str, Any] | None = None


class BrainQueryResponse(BaseModel):
    """Response returned by the Personal Brain after processing a query."""

    answer: str
    source: str = "mock_personal_brain_provider"
    context_used: bool = False
    user_id: str | None = None
    model: str | None = None
    latency_ms: int | None = None
    tokens_used: int | None = None


class BrainIngestRequest(BaseModel):
    """Request to ingest processed application data into the Personal Brain."""

    content: str = Field(..., min_length=1, max_length=200000)
    content_type: str = Field(default="text")
    source_app: str | None = None
    metadata: dict[str, Any] | None = None


class BrainIngestResponse(BaseModel):
    """Response for brain ingestion."""

    accepted: bool = True
    classification: dict[str, Any]
    stored: bool = True
