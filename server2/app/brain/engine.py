from __future__ import annotations

import uuid
from typing import Any

from app.brain.context import build_brain_prompt
from app.providers.brain_llm import QwenBrainEngine
from app.providers.vault import VaultProvider


class BrainService:
    def __init__(self, llm: QwenBrainEngine, vault_provider: VaultProvider | None = None):
        self.llm = llm
        self.vault_provider = vault_provider

    def validate_identity(self, aura_id: str, brain_id: str, context: dict[str, Any]) -> None:
        expected_aura = (context or {}).get("aura_id")
        expected_brain = (context or {}).get("brain_id")
        if expected_aura and expected_aura != aura_id:
            raise ValueError("Request Aura ID does not match the context Aura ID.")
        if expected_brain and expected_brain != brain_id:
            raise ValueError("Request Brain ID does not match the context Brain ID.")

    def process(self, aura_id: str, brain_id: str, query: str, context: dict[str, Any]) -> dict[str, Any]:
        if not aura_id or not brain_id or not query:
            raise ValueError("Aura ID, Brain ID, and query are required.")

        self.validate_identity(aura_id, brain_id, context)

        vault_context = None
        if self.vault_provider is not None:
            vault_context = self.vault_provider.get_user_context(aura_id)

        prompt = build_brain_prompt(aura_id, brain_id, query, context, vault_context)
        response_text = self.llm.generate(prompt)

        if self.vault_provider is not None:
            self.vault_provider.store_brain_output(aura_id, {"response": response_text, "brain_id": brain_id})

        return {
            "aura_id": aura_id,
            "brain_id": brain_id,
            "response": response_text,
            "model": "Qwen3.5-4B",
            "request_id": str(uuid.uuid4()),
            "status": "ok",
        }
