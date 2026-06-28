import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from .config import settings

_CF_BASE = "https://gateway.ai.cloudflare.com/v1"
_OPENROUTER_DIRECT = "https://openrouter.ai/api/v1/chat/completions"
_TIMEOUT = 60.0


def _build_url(account_id: str, gateway_id: str) -> str:
    if account_id and gateway_id:
        return f"{_CF_BASE}/{account_id}/{gateway_id}/openrouter/v1/chat/completions"
    return _OPENROUTER_DIRECT


async def chat_completion(
    messages: list[dict],
    model: str,
    openrouter_key: str,
    *,
    account_id: str | None = None,
    gateway_id: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.1,
) -> dict[str, Any]:
    url = _build_url(
        account_id or settings.cf_account_id,
        gateway_id or settings.cf_gateway_id,
    )
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://rag-demos",
        "X-Title": "RAG Demos",
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return {
        "text": text,
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
    }


async def chat_completion_stream(
    messages: list[dict],
    model: str,
    openrouter_key: str,
    *,
    account_id: str | None = None,
    gateway_id: str | None = None,
    max_tokens: int = 2500,
    temperature: float = 0.1,
) -> AsyncIterator[dict[str, Any]]:
    """Stream a chat completion. Yields {"type": "delta", "text": ...} for each
    content chunk, then a final {"type": "done", "usage": {...}}."""
    url = _build_url(
        account_id or settings.cf_account_id,
        gateway_id or settings.cf_gateway_id,
    )
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://rag-demos",
        "X-Title": "RAG Demos",
    }
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if not data_str or data_str == "[DONE]":
                    continue
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
                if chunk.get("usage"):
                    u = chunk["usage"]
                    usage = {
                        "prompt_tokens": u.get("prompt_tokens", 0),
                        "completion_tokens": u.get("completion_tokens", 0),
                        "total_tokens": u.get("total_tokens", 0),
                    }
                choices = chunk.get("choices") or []
                if choices:
                    delta = choices[0].get("delta") or {}
                    text = delta.get("content")
                    if text:
                        yield {"type": "delta", "text": text}
    yield {"type": "done", "usage": usage}
