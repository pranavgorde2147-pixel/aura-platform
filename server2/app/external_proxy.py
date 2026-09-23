from __future__ import annotations

import os
import re
from typing import Any

from groq import Groq
from groq.types.chat import ChatCompletionChunk


def _strip_thinking_tags(text: str) -> str:
    """Remove  thinking... response blocks (including unclosed ones) from model output."""
    text = re.sub(r" thinking.*? response", "", text, flags=re.DOTALL).strip()
    text = re.sub(r" thinking.*", "", text, flags=re.DOTALL).strip()
    return text


def _build_client() -> Groq:
    """Build a Groq client from EXTERNAL_AI_KEY or GROQ_API_KEY."""
    key = os.getenv("EXTERNAL_AI_KEY", "").strip() or os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("External AI provider not configured (EXTERNAL_AI_KEY/GROQ_API_KEY)")
    return Groq(api_key=key)


def call_external_model(prompt: str) -> str:
    """Call Groq (OpenAI-compatible) via the Python SDK and return the text reply.

    Expects environment variables:
    - EXTERNAL_AI_KEY (or GROQ_API_KEY) - Groq bearer token
    - EXTERNAL_MODEL (model id, e.g. qwen/qwen3.8-27b)
    """
    model_name = os.getenv("EXTERNAL_MODEL", "qwen/qwen3.8-27b").strip()
    temperature = float(os.getenv("TEMPERATURE", "0.6"))
    max_tokens = int(os.getenv("MAX_NEW_TOKENS", "2048"))
    top_p = float(os.getenv("TOP_P", "0.95"))

    stream = _build_client().chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=top_p,
        reasoning_effort="default",
        stream=True,
        stop=None,
    )

    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta is None:
            continue
        reasoning_content = getattr(delta, "reasoning_content", None)
        if isinstance(reasoning_content, str) and reasoning_content:
            reasoning_parts.append(reasoning_content)
        if delta.content:
            content_parts.append(delta.content)

    content = "".join(content_parts).strip()
    if content:
        return content
    reasoning = _strip_thinking_tags("".join(reasoning_parts)).strip()
    return reasoning or "I could not produce a response."