from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from .condense import condense_query
from .config import settings
from .gateway import chat_completion
from .rerank import rerank
from .retrieval import retrieve

router = APIRouter()

REPO_ROOT = Path(__file__).parent.parent.parent.parent
_GEN_MODEL = settings.gen_model
_EMBED_MODEL = settings.embed_model


def _load_system_prompt(demo_id: str, version: str) -> str:
    path = REPO_ROOT / "demos" / demo_id / "prompts" / f"system_{version}.md"
    if not path.exists():
        raise ValueError(f"System prompt not found for demo={demo_id!r} version={version!r} at {path}")
    return path.read_text()


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(
            f"[{c['section_ref']} — {c['doc_title']}]\n{c['content']}"
        )
    return "\n\n---\n\n".join(parts)


def _assemble_citations(chunks: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    citations = []
    for c in chunks:
        key = (c["doc_id"], c["section_ref"])
        if key not in seen:
            seen.add(key)
            citations.append({"section_ref": c["section_ref"], "doc_title": c["doc_title"]})
    return citations


class Turn(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    q: str
    history: list[Turn] = Field(default_factory=list)


class QueryResponse(BaseModel):
    answer: str
    retrieved_chunks: list[dict]
    citations: list[dict]
    config: dict
    usage: dict
    latency: dict
    trace_id: str


@router.post("/api/{demo}/query", response_model=QueryResponse)
async def query(
    demo: str,
    req: QueryRequest,
    mode: str = "hybrid",
    top_k: int = 20,
    top_n: int = 5,
    do_rerank: bool = True,
    gen_model: str | None = None,
    reranker_model: str | None = None,
    prompt_version: str = "v1",
    cf_account_id: str | None = None,
    cf_gateway_id: str | None = None,
    x_openrouter_key: Annotated[str | None, Header()] = None,
):
    if not x_openrouter_key:
        raise HTTPException(status_code=401, detail="X-OpenRouter-Key header required")

    demo_id = demo.lower()

    trace_id = str(uuid.uuid4())
    t_start = time.perf_counter()

    # condense
    t0 = time.perf_counter()
    history = [t.model_dump() for t in req.history]
    effective_q = await condense_query(
        req.q, history, x_openrouter_key,
        account_id=cf_account_id, gateway_id=cf_gateway_id,
    )
    condense_ms = int((time.perf_counter() - t0) * 1000)

    # retrieve
    t0 = time.perf_counter()
    chunks = await retrieve(
        effective_q,
        demo_id=demo_id,
        mode=mode,
        top_k=top_k,
        openrouter_key=x_openrouter_key,
        hyde_model=None,
        cf_account_id=cf_account_id,
        cf_gateway_id=cf_gateway_id,
    )
    retrieve_ms = int((time.perf_counter() - t0) * 1000)

    # rerank → top_n
    t0 = time.perf_counter()
    rerank_ms = 0
    if do_rerank and chunks:
        chunks = await rerank(
            effective_q, chunks, top_n, x_openrouter_key,
            account_id=cf_account_id, gateway_id=cf_gateway_id,
            model=reranker_model,
        )
        rerank_ms = int((time.perf_counter() - t0) * 1000)
    else:
        chunks = chunks[:top_n]

    # generate
    t0 = time.perf_counter()
    model = gen_model or _GEN_MODEL
    system_tmpl = _load_system_prompt(demo_id, prompt_version)
    context_str = _build_context(chunks)
    system_msg = system_tmpl.replace("{context}", context_str)

    messages = [{"role": "system", "content": system_msg}]
    for turn in req.history[-10:]:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": req.q})

    gen_result = await chat_completion(
        messages=messages,
        model=model,
        openrouter_key=x_openrouter_key,
        account_id=cf_account_id,
        gateway_id=cf_gateway_id,
    )
    generate_ms = int((time.perf_counter() - t0) * 1000)
    total_ms = int((time.perf_counter() - t_start) * 1000)

    return QueryResponse(
        answer=gen_result["text"],
        retrieved_chunks=[
            {
                "id": c["id"],
                "doc_id": c["doc_id"],
                "doc_title": c["doc_title"],   # additive — server-authoritative label
                "section_ref": c["section_ref"],
                "content": c["content"][:400],
                "score": c.get("score", 0.0),
                "rerank_score": c.get("rerank_score"),
            }
            for c in chunks
        ],
        citations=_assemble_citations(chunks),
        config={
            "demo": demo_id,
            "mode": mode,
            "top_k": top_k,
            "top_n": top_n,
            "rerank": do_rerank,
            "gen_model": model,
            "reranker_model": reranker_model or settings.reranker_model,
            "embed_model": _EMBED_MODEL,
            "prompt_version": prompt_version,
        },
        usage=gen_result["usage"],
        latency={
            "condense_ms": condense_ms,
            "retrieve_ms": retrieve_ms,
            "rerank_ms": rerank_ms,
            "generate_ms": generate_ms,
            "total_ms": total_ms,
        },
        trace_id=trace_id,
    )
