from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class VaultProvider(ABC):
    @abstractmethod
    def get_user_context(self, aura_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def search_user_memory(self, aura_id: str, query: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def store_brain_output(self, aura_id: str, data: dict[str, Any]) -> None:
        raise NotImplementedError


class MockVaultProvider(VaultProvider):
    def __init__(self) -> None:
        self._memory: dict[str, list[str]] = {}

    def get_user_context(self, aura_id: str) -> dict[str, Any]:
        return {
            "aura_id": aura_id,
            "notes": self._memory.get(aura_id, ["No vault context available yet."]),
        }

    def search_user_memory(self, aura_id: str, query: str) -> list[str]:
        memory = self._memory.get(aura_id, [])
        if not memory:
            return ["No user context available in the mock vault."]
        return [entry for entry in memory if query.lower() in entry.lower()] or memory[:3]

    def store_brain_output(self, aura_id: str, data: dict[str, Any]) -> None:
        self._memory.setdefault(aura_id, []).append(str(data.get("response", "")))
