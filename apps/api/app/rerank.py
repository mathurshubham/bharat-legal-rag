"""
API-only reranker — no local model.
Default: Cohere Rerank v3.5 (direct or via Cloudflare AI Gateway).
No Cohere key → skip reranking, caller takes top_n direct from retrieval.
"""
import os
from typing import Any

import httpx

_CF_BASE = "https://gateway.ai.cloudflare.com/v1"
_COHERE_DIRECT = "https://api.cohere.com/v2/rerank"
_COHERE_MODEL = os.getenv("RERANKER_MODEL", "rerank-v3.5")
_TIMEOUT = 30.0


def _cohere_url(account_id: str, gateway_id: str) -> str:
    if account_id and gateway_id:
        return f"{_CF_BASE}/{account_id}/{gateway_id}/cohere/v2/rerank"
    return _COHERE_DIRECT


async def rerank(
    query: str,
    chunks: list[dict],
    top_n: int,
    cohere_key: str,
    *,
    account_id: str | None = None,
    gateway_id: str | None = None,
) -> list[dict]:
    if not chunks:
        return chunks

    url = _cohere_url(
        account_id or os.getenv("CF_ACCOUNT_ID", ""),
        gateway_id or os.getenv("CF_GATEWAY_ID", ""),
    )
    docs = [c["content"] for c in chunks]

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {cohere_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _COHERE_MODEL,
                "query": query,
                "documents": docs,
                "top_n": top_n,
            },
        )
    resp.raise_for_status()
    results = resp.json()["results"]

    out = []
    for r in results:
        chunk = dict(chunks[r["index"]])
        chunk["rerank_score"] = r["relevance_score"]
        out.append(chunk)
    return out
