"""
Retrieval modes: vanilla, bm25, hybrid (RRF), hyde.

All modes tested in production.
vanilla  = dense kNN only
bm25     = BM25 full-text only
hybrid   = dense + BM25 → RRF fusion (default)
hyde     = generate hypothetical doc → embed → dense kNN
"""
from __future__ import annotations

import asyncio

import psycopg
from psycopg.rows import dict_row

from .db import get_pool
from .embed import embed_query

RRF_K = 60

_HYDE_PROMPT = (
    "You are a legal drafting assistant. Write a short excerpt (2-4 sentences) from an "
    "Indian statute or legal provision that would directly answer the following question. "
    "Write only the provision text, no preamble.\n\nQuestion: {query}"
)


async def _dense(conn: psycopg.AsyncConnection, vec: list[float], top_k: int) -> list[dict]:
    cur = await conn.execute(
        """
        SELECT id, doc_id, doc_title, section_ref, content,
               1 - (embedding <=> %s::vector) AS score
        FROM chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (vec, vec, top_k),
    )
    return await cur.fetchall()


async def _bm25(conn: psycopg.AsyncConnection, query: str, top_k: int) -> list[dict]:
    cur = await conn.execute(
        """
        SELECT id, doc_id, doc_title, section_ref, content,
               paradedb.score(id) AS score
        FROM chunks
        WHERE content @@@ %s
        ORDER BY score DESC
        LIMIT %s
        """,
        (query, top_k),
    )
    return await cur.fetchall()


def _rrf(dense_rows: list[dict], bm25_rows: list[dict], top_k: int) -> list[dict]:
    scores: dict[int, float] = {}
    by_id: dict[int, dict] = {}

    for rank, row in enumerate(dense_rows):
        rid = row["id"]
        scores[rid] = scores.get(rid, 0.0) + 1.0 / (RRF_K + rank + 1)
        by_id[rid] = row

    for rank, row in enumerate(bm25_rows):
        rid = row["id"]
        scores[rid] = scores.get(rid, 0.0) + 1.0 / (RRF_K + rank + 1)
        by_id.setdefault(rid, row)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    result = []
    for rid, rrf_score in ranked:
        row = dict(by_id[rid])
        row["score"] = rrf_score
        result.append(row)
    return result


async def retrieve(
    query: str,
    mode: str = "hybrid",
    top_k: int = 20,
    *,
    openrouter_key: str | None = None,
    hyde_model: str | None = None,
    cf_account_id: str | None = None,
    cf_gateway_id: str | None = None,
) -> list[dict]:
    pool = await get_pool()
    async with pool.connection() as conn:
        conn.row_factory = dict_row

        if mode == "vanilla":
            vec = embed_query([query])[0]
            return await _dense(conn, vec, top_k)

        if mode == "bm25":
            return await _bm25(conn, query, top_k)

        if mode == "hybrid":
            vec = embed_query([query])[0]
            dense_rows, bm25_rows = await asyncio.gather(
                _dense(conn, vec, top_k),
                _bm25(conn, query, top_k),
            )
            return _rrf(dense_rows, bm25_rows, top_k)

        if mode == "hyde":
            from .gateway import chat_completion
            import os
            model = hyde_model or os.getenv("HYDE_MODEL", "google/gemma-4-31b-it:free")
            key = openrouter_key or ""
            result = await chat_completion(
                messages=[{"role": "user", "content": _HYDE_PROMPT.format(query=query)}],
                model=model,
                openrouter_key=key,
                account_id=cf_account_id,
                gateway_id=cf_gateway_id,
                max_tokens=256,
                temperature=0.3,
            )
            hypothetical_doc = result["text"].strip()
            vec = embed_query([hypothetical_doc])[0]
            return await _dense(conn, vec, top_k)

        raise ValueError(f"Unknown retrieval mode: {mode!r}")
