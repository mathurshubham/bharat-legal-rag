import os
from typing import Any

from sentence_transformers import CrossEncoder

_MODEL_ID = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(_MODEL_ID, max_length=512)
    return _reranker


def rerank(query: str, chunks: list[dict], top_n: int) -> list[dict]:
    if not chunks:
        return chunks
    model = get_reranker()
    pairs = [(query, c["content"]) for c in chunks]
    scores = model.predict(pairs, show_progress_bar=False).tolist()
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)
    ranked = sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)
    return ranked[:top_n]


async def rerank_with_cohere(
    query: str,
    chunks: list[dict],
    top_n: int,
    cohere_key: str,
) -> list[dict]:
    import httpx

    docs = [c["content"] for c in chunks]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.cohere.com/v2/rerank",
            headers={"Authorization": f"Bearer {cohere_key}", "Content-Type": "application/json"},
            json={"model": "rerank-v3.5", "query": query, "documents": docs, "top_n": top_n},
        )
    resp.raise_for_status()
    results = resp.json()["results"]
    out = []
    for r in results:
        chunk = dict(chunks[r["index"]])
        chunk["rerank_score"] = r["relevance_score"]
        out.append(chunk)
    return out
