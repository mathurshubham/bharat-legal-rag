"""
Retrieval modes: vanilla, bm25, hybrid (RRF), hyde (stub).

Tested in production: hybrid
Wired but untested until stretch mode-switcher: vanilla, bm25
Explicit stub (needs gateway round-trip): hyde
"""
from __future__ import annotations

import asyncio
from typing import Any

import psycopg
from psycopg.rows import dict_row

from .db import get_pool
from .embed import embed_query

RRF_K = 60


async def _dense(
    conn: psycopg.AsyncConnection,
    vec: list[float],
    top_k: int,
) -> list[dict]:
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


async def _bm25(
    conn: psycopg.AsyncConnection,
    query: str,
    top_k: int,
) -> list[dict]:
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


def _rrf(
    dense_rows: list[dict],
    bm25_rows: list[dict],
    top_k: int,
) -> list[dict]:
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
            dense_task = _dense(conn, vec, top_k)
            bm25_task = _bm25(conn, query, top_k)
            dense_rows, bm25_rows = await asyncio.gather(dense_task, bm25_task)
            return _rrf(dense_rows, bm25_rows, top_k)

        if mode == "hyde":
            # stub — needs gateway round-trip to generate hypothetical doc
            raise NotImplementedError("HyDE is a stretch feature, not yet implemented")

        raise ValueError(f"Unknown retrieval mode: {mode!r}")
