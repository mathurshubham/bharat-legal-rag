"""
API-only reranker via OpenRouter native rerank endpoint.
URL: POST https://openrouter.ai/api/v1/rerank
Same OpenRouter key as generation — no separate Cohere key needed.
Also routes through Cloudflare AI Gateway when CF creds are present.

Default model: nvidia/llama-nemotron-rerank-vl-1b-v2:free (free tier)
Override: RERANKER_MODEL env var
"""
import os

import httpx

_CF_BASE = "https://gateway.ai.cloudflare.com/v1"
_OR_DIRECT = "https://openrouter.ai/api/v1/rerank"
_DEFAULT_MODEL = os.getenv("RERANKER_MODEL", "nvidia/llama-nemotron-rerank-vl-1b-v2:free")
_TIMEOUT = 30.0


def _rerank_url(account_id: str, gateway_id: str) -> str:
    if account_id and gateway_id:
        # CF AI Gateway → OpenRouter rerank path
        return f"{_CF_BASE}/{account_id}/{gateway_id}/openrouter/api/v1/rerank"
    return _OR_DIRECT


async def rerank(
    query: str,
    chunks: list[dict],
    top_n: int,
    openrouter_key: str,
    *,
    account_id: str | None = None,
    gateway_id: str | None = None,
    model: str | None = None,
) -> list[dict]:
    if not chunks:
        return chunks

    url = _rerank_url(
        account_id or os.getenv("CF_ACCOUNT_ID", ""),
        gateway_id or os.getenv("CF_GATEWAY_ID", ""),
    )
    docs = [c["content"] for c in chunks]

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://legal-rag-demo",
                "X-Title": "Legal RAG Demo",
            },
            json={
                "model": model or _DEFAULT_MODEL,
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
