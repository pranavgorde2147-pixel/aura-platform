"""Real Brain LLM provider that calls Server 2 Brain inference service."""

from __future__ import annotations

import logging
from typing import Any

from app.infrastructure.brain_client import get_brain_client
from app.models.user import User

logger = logging.getLogger(__name__)


class RealPersonalBrainLLMProvider:
    """Real implementation of PersonalBrainLLMProvider that calls Server 2."""

    async def process_query(
        self,
        user: User,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a query by calling Server 2 Brain inference service."""
        context = context or {}
        client = get_brain_client()

        try:
            response = await client.infer(
                user_id=str(user.id),
                query=query,
                context=context,
            )
            return {
                "answer": response.get("response", ""),
                "source": "server2_brain",
                "context_used": bool(context),
                "user_id": str(user.id),
                "model": response.get("model"),
                "latency_ms": response.get("latency_ms"),
                "tokens_used": response.get("tokens_used"),
            }
        except Exception as e:
            logger.error(f"Failed to process query via Server 2: {e}")
            return {
                "answer": f"Error: Unable to process query - {str(e)}",
                "source": "server2_error",
                "context_used": False,
                "user_id": str(user.id),
                "error": str(e),
            }

    async def classify_information(
        self,
        user: User,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Classify incoming data (currently uses simple local classification)."""
        content = payload.get("content", "")
        content_type = payload.get("content_type", "text")
        return {
            "user_id": str(user.id),
            "content_type": content_type,
            "labels": ["personal_brain_ingest", "classified"],
            "summary": f"Received {content_type} for {user.email}: {str(content)[:120]}",
            "source_app": payload.get("source_app"),
        }

    async def prepare_external_context(
        self,
        user: User,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build minimal context for external LLM processing."""
        context = context or {}
        relevant = {
            key: value
            for key, value in context.items()
            if key in {"schedule", "goals", "known_topics", "user_level"}
        }
        return {
            "user_id": str(user.id),
            "query": query,
            "user_level": context.get("user_level", "general"),
            "relevant_context": relevant,
            "safety_constraints": [
                "never_forward_full_vault",
                "only_send_minimal_context",
            ],
        }

    async def personalize_response(
        self,
        user: User,
        base_answer: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Personalize the response with user context."""
        context = context or {}
        context_keys = ", ".join(sorted(context.keys())) if context else "none"
        return f"{base_answer}\n\n[Personalized for {user.email} | Context: {context_keys}]"
