from __future__ import annotations

from typing import Any


def build_brain_prompt(aura_id: str, brain_id: str, query: str, context: dict[str, Any], vault_context: dict[str, Any] | None = None) -> str:
    safe_context = {k: v for k, v in (context or {}).items() if k not in {"vault", "password", "secret", "token", "jwt"}}
    vault_block = ""
    if vault_context:
        vault_block = "\nVault context:\n" + str(vault_context)

    return (
        "You are the AURA Personal Brain for this user. "
        "Reason using the provided personal context and user query. "
        "Do not invent facts. Be concise, practical, and personalized.\n\n"
        f"Aura ID: {aura_id}\n"
        f"Brain ID: {brain_id}\n"
        f"User query: {query}\n"
        f"Additional context: {safe_context}\n"
        f"{vault_block}\n"
        "Answer directly in plain language."
    )
