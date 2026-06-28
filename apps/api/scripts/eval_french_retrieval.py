#!/usr/bin/env python3
"""French retrieval-only eval for golden_sets/french-v2-dataset.csv.

This deliberately bypasses answer generation. It measures whether retrieval and
rerank surface the right textbook chunks before the LLM has a chance to help or
hide the failure.

Run:
  DATABASE_URL=... OPENROUTER_API_KEY=... \
    uv run --project apps/api python apps/api/scripts/eval_french_retrieval.py

Optional:
  uv run --project apps/api python apps/api/scripts/eval_french_retrieval.py --no-rerank
  uv run --project apps/api python apps/api/scripts/eval_french_retrieval.py --category grammar
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "apps/api"))

from app.config import settings  # noqa: E402
from app.db import close_pool  # noqa: E402
from app.query import (  # noqa: E402
    _boost_french_chunks,
    _detect_french_chapter,
    _detect_french_intent,
)
from app.rerank import rerank  # noqa: E402
from app.retrieval import retrieve  # noqa: E402


DATASET = REPO_ROOT / "golden_sets" / "french-v2-dataset.csv"
OUT_DIR = REPO_ROOT / "runs"


def _split_pipe(value: str) -> list[str]:
    return [v.strip() for v in (value or "").split("|") if v.strip()]


@dataclass
class Case:
    category: str
    query: str
    expected_doc_ids: list[str]
    expected_section_substrings: list[str]
    expected_keywords: list[str]
    expected_types: list[str]
    expected_board: str
    expected_chapter: str
    should_refuse: bool
    notes: str


def load_cases(path: Path, category: str | None) -> list[Case]:
    with path.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    cases = []
    for row in rows:
        cat = row["eval_context"]
        if category and cat != category:
            continue
        cases.append(Case(
            category=cat,
            query=row["input"],
            expected_doc_ids=_split_pipe(row["expected_doc_ids"]),
            expected_section_substrings=_split_pipe(row["expected_section_substrings"]),
            expected_keywords=_split_pipe(row["expected_keywords"]),
            expected_types=[t.lower() for t in _split_pipe(row["expected_types"])],
            expected_board=row["expected_board"].strip().lower(),
            expected_chapter=row["expected_chapter"].strip(),
            should_refuse=row["should_refuse"].strip().lower() == "true",
            notes=row.get("notes", ""),
        ))
    return cases


def chunk_text(chunk: dict) -> str:
    meta = chunk.get("metadata") or {}
    header = meta.get("header_path", "") if isinstance(meta, dict) else ""
    return " ".join([
        str(chunk.get("section_ref", "")),
        str(header),
        str(chunk.get("content", "")),
    ]).lower()


def chunk_type(chunk: dict) -> str:
    meta = chunk.get("metadata") or {}
    if isinstance(meta, dict):
        return str(meta.get("type") or "").lower()
    return ""


def chunk_board(chunk: dict) -> str:
    meta = chunk.get("metadata") or {}
    if isinstance(meta, dict):
        return str(meta.get("board") or "").lower()
    return ""


def is_relevant(case: Case, chunk: dict) -> bool:
    if case.expected_doc_ids and chunk.get("doc_id") not in case.expected_doc_ids:
        return False

    text = chunk_text(chunk)
    if case.expected_section_substrings:
        section_hit = any(s.lower() in text for s in case.expected_section_substrings)
        if not section_hit:
            return False

    if not case.expected_section_substrings and case.expected_keywords:
        keyword_hit = any(k.lower() in text for k in case.expected_keywords)
        if not keyword_hit:
            return False

    return True


def first_rank(case: Case, chunks: list[dict]) -> int | None:
    for i, chunk in enumerate(chunks, 1):
        if is_relevant(case, chunk):
            return i
    return None


def has_type(case: Case, chunks: list[dict], k: int) -> bool:
    if not case.expected_types:
        return True
    return any(chunk_type(c) in case.expected_types for c in chunks[:k])


def board_leak(case: Case, chunks: list[dict]) -> bool:
    if case.expected_board not in ("cbse", "ib"):
        return False
    return any((b := chunk_board(c)) and b != case.expected_board for c in chunks)


def chapter_hit(case: Case, chunks: list[dict], k: int) -> bool:
    if not case.expected_chapter:
        return True
    needle = case.expected_chapter.lower()
    return any(needle in chunk_text(c) for c in chunks[:k])


def summarize(results: list[dict], top_n: int) -> dict:
    answerable = [r for r in results if not r["should_refuse"]]
    denom = max(1, len(answerable))
    ranks = [r["final_rank"] for r in answerable if r["final_rank"]]
    return {
        "cases": len(results),
        "answerable_cases": len(answerable),
        "candidate_hit_at_40": round(sum(r["candidate_rank"] is not None and r["candidate_rank"] <= 40 for r in answerable) / denom, 3),
        f"final_hit_at_{top_n}": round(sum(r["final_rank"] is not None and r["final_rank"] <= top_n for r in answerable) / denom, 3),
        "mrr_final": round(sum(1 / r for r in ranks) / denom, 3),
        f"type_hit_at_{top_n}": round(sum(r["type_hit"] for r in answerable) / denom, 3),
        f"chapter_hit_at_{top_n}": round(sum(r["chapter_hit"] for r in answerable) / denom, 3),
        "board_leak_cases": sum(r["board_leak"] for r in results),
        "avg_latency_ms": round(sum(r["latency_ms"] for r in results) / max(1, len(results))),
    }


async def eval_case(case: Case, args: argparse.Namespace) -> dict:
    t0 = time.perf_counter()
    board = None if case.expected_board in ("", "all") else case.expected_board
    chapter = _detect_french_chapter(case.query, case.expected_chapter) or case.expected_chapter or None
    intent = _detect_french_intent(case.query)

    candidates = await retrieve(
        case.query,
        demo_id="french",
        mode=args.mode,
        top_k=args.top_k,
        visibility=["public"],
        openrouter_key=settings.openrouter_api_key,
        board=board,
        section_filter=None,
    )
    candidates = _boost_french_chunks(candidates, chapter_filter=chapter, intent=intent)
    final = candidates[:args.top_n]

    if args.rerank and candidates:
        rerank_top_n = args.top_n
        if intent.get("grammar"):
            rerank_top_n = min(len(candidates), max(args.top_n * 3, 15))
        final = await rerank(
            case.query,
            candidates,
            rerank_top_n,
            settings.openrouter_api_key,
            model=args.reranker_model,
        )
        final = _boost_french_chunks(final, chapter_filter=chapter, intent=intent)[:args.top_n]

    latency_ms = round((time.perf_counter() - t0) * 1000)
    c_rank = first_rank(case, candidates)
    f_rank = first_rank(case, final)
    return {
        "category": case.category,
        "query": case.query,
        "should_refuse": case.should_refuse,
        "candidate_rank": c_rank,
        "final_rank": f_rank,
        "type_hit": has_type(case, final, args.top_n),
        "chapter_hit": chapter_hit(case, final, args.top_n),
        "board_leak": board_leak(case, final),
        "latency_ms": latency_ms,
        "top_final": [
            {
                "doc_id": c.get("doc_id"),
                "section_ref": c.get("section_ref"),
                "type": chunk_type(c),
                "board": chunk_board(c),
                "boost": c.get("retrieval_boost"),
                "reasons": c.get("boost_reasons", []),
            }
            for c in final[: args.top_n]
        ],
        "notes": case.notes,
    }


async def main_async(args: argparse.Namespace) -> int:
    cases = load_cases(args.dataset, args.category)
    if not cases:
        print("No cases matched.")
        return 2

    results = []
    for i, case in enumerate(cases, 1):
        try:
            result = await eval_case(case, args)
        except Exception as exc:  # keep the run useful when one case fails
            result = {
                "category": case.category,
                "query": case.query,
                "should_refuse": case.should_refuse,
                "error": repr(exc),
                "candidate_rank": None,
                "final_rank": None,
                "type_hit": False,
                "chapter_hit": False,
                "board_leak": False,
                "latency_ms": 0,
                "top_final": [],
            }
        results.append(result)
        status = "SKIP" if case.should_refuse else ("HIT" if result.get("final_rank") else "MISS")
        print(
            f"[{i:02}/{len(cases)}] {status:4} {case.category:8} "
            f"cand={result.get('candidate_rank')} final={result.get('final_rank')} "
            f"type={result.get('type_hit')} chapter={result.get('chapter_hit')} "
            f"{case.query[:80]}"
        )

    summary = summarize(results, args.top_n)
    print("\n=== SUMMARY ===")
    for key, value in summary.items():
        print(f"{key}: {value}")

    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / f"french-retrieval-{int(time.time())}.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"\nWrote {out_path}")

    await close_pool()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--category")
    parser.add_argument("--mode", choices=["hybrid", "vanilla", "bm25", "hyde"], default="hybrid")
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--top-n", type=int, default=8)
    parser.add_argument("--rerank", dest="rerank", action="store_true", default=True)
    parser.add_argument("--no-rerank", dest="rerank", action="store_false")
    parser.add_argument("--reranker-model", default=None)
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
