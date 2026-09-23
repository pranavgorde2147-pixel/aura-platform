"""Personal Brain API boundary for app-to-brain communication."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.infrastructure.database.session import get_db
from app.models.user import User
from app.schemas.brain import BrainIngestRequest, BrainIngestResponse, BrainQueryRequest, BrainQueryResponse
from app.services.personal_brain import PersonalBrainService

router = APIRouter(prefix="/brain", tags=["Brain"])


@router.post("/query", response_model=BrainQueryResponse)
async def query_brain(
    payload: BrainQueryRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> BrainQueryResponse:
    """Process a user query through their Personal Brain."""
    service = PersonalBrainService(session)
    result = await service.process_query(current_user, payload.query, payload.context or {})
    return BrainQueryResponse(**result)


@router.post("/ingest", response_model=BrainIngestResponse)
async def ingest_to_brain(
    payload: BrainIngestRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> BrainIngestResponse:
    """Send application-generated data to the user's Personal Brain for classification."""
    service = PersonalBrainService(session)
    result = await service.ingest_data(current_user, payload.model_dump())
    return BrainIngestResponse(**result)


@router.get("/context")
async def brain_context(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Return the current user's brain context in a protected endpoint."""
    service = PersonalBrainService(session)
    brain = await service.get_brain_for_user(current_user.id)
    if brain is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal brain not found")
    return await service.get_brain_context(brain.ai_identity_id)
