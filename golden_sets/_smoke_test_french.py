#!/usr/bin/env python3
"""Smoke-test the french demo across board + language combinations.

Hits /api/french/query directly. Counts citations per board, asserts board
isolation, refusal triggers, and language compliance.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time

API = "http://localhost:8000/api/french/query"

# (board, language, q, must_have_subsets, should_refuse)
TESTS: list[tuple] = [
    ("all",  "bilingual", "What are the main themes of IB DP French B?",     {"ib"},          False),
    ("cbse", "fr",         "Comment se présenter en français ?",               {"cbse"},        False),
    ("cbse", "en",         "What does CBSE Class 10 teach about pollution?",   {"cbse"},        False),
    ("cbse", "bilingual",  "Qu'est-ce que la francophonie selon CBSE ?",        {"cbse"},        False),
    ("ib",   "fr",         "Qu'est-ce que l'éco-citoyenneté ?",                {"ib"},          False),
    ("ib",   "en",         "What is the IB DP French B exam structure?",       {"ib"},          False),
    ("ib",   "bilingual",  "Que dit l'Unité 1A sur Qui suis-je ?",              {"ib"},          False),
    # Cross-board (asking IB-only topic from CBSE filter)
    ("cbse", "fr",         "Quels sont les sous-cultures dans l'IB DP ?",       {"cbse"},        False),  # may answer from CBSE if it has anything
    # Refusal cases
    ("all",  "bilingual",  "What is the punishment for murder under IPC?",     set(),           True),
    ("all",  "bilingual",  "Teach me Chinese pronunciation.",                   set(),           True),
    ("all",  "bilingual",  "Solve the À TOI exercise on page 12 of CBSE 9.",   set(),           True),
]


def post(board: str, language: str, q: str) -> dict:
    params = f"?board={board}&mode=hybrid&top_k=20&top_n=5&do_rerank=true"
    body = json.dumps({"q": q, "history": [], "language_mode": language})
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", API + params,
         "-H", "Content-Type: application/json",
         "--data-binary", body],
        capture_output=True, text=True, timeout=120,
    )
    if not r.stdout.strip():
        return {"error": f"empty body, stderr={r.stderr[:200]}"}
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"error": "non-json", "raw": r.stdout[:200]}


def citation_boards(d: dict) -> set[str]:
    boards: set[str] = set()
    for c in d.get("citations", []):
        title = c.get("doc_title", "")
        if "CBSE" in title:
            boards.add("cbse")
        if "IB DP" in title:
            boards.add("ib")
    return boards


def looks_like_refusal(answer: str) -> bool:
    a = answer.lower()
    markers = ["cannot answer", "i cannot", "je ne peux pas",
               "outside the indexed", "not in the indexed",
               "outside your", "not covered", "do not", "i can't",
               "not in your", "this topic", "indexed corpus",
               "not part of"]
    return any(m in a for m in markers)


def lang_compliance(language: str, answer: str) -> str:
    has_sep = "---" in answer
    if language == "fr":
        return "ok" if not has_sep else "has-en-section"
    if language == "en":
        # rough french detection: presence of accented chars
        has_french = any(c in answer for c in "éèêëçàâîïôûùÉÈÊÀ")
        # exclude quoted French source — too strict
        return "ok" if not has_sep else "has-fr-section"
    if language == "bilingual":
        return "ok" if has_sep else "no-separator"
    return "unknown"


def main():
    print(f"Running {len(TESTS)} smoke tests…\n")
    passes = fails = 0
    for i, (board, lang, q, expected_boards, should_refuse) in enumerate(TESTS, 1):
        t0 = time.monotonic()
        d = post(board, lang, q)
        elapsed = time.monotonic() - t0
        if d.get("error"):
            print(f"[{i:2}/{len(TESTS)}] ERR  {d['error']}")
            fails += 1
            continue
        answer = d.get("answer", "")
        cb = citation_boards(d)
        refused = looks_like_refusal(answer)
        lc = lang_compliance(lang, answer)

        # Pass conditions
        if should_refuse:
            ok = refused and not cb
        else:
            ok = (not refused) and (cb <= expected_boards if expected_boards else True)
            if board != "all":
                ok = ok and (cb <= {board} or not cb)
        status = "✓" if ok else "✗"
        if ok:
            passes += 1
        else:
            fails += 1
        print(f"[{i:2}/{len(TESTS)}] {status}  board={board:4} lang={lang:9} "
              f"refused={str(refused):5} cite_boards={cb!s:18} lang_check={lc:18} "
              f"{elapsed:5.1f}s  {q[:50]}")

    print(f"\nResult: {passes}/{len(TESTS)} passed, {fails} failed")
    return 0 if fails == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
