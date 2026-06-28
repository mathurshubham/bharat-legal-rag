#!/usr/bin/env python3
"""Question-generation QUALITY eval (LLM-as-judge).

Distinct from eval_french_retrieval.py (which scores retrieval recall). This
scores the *generated question bank* against board-authentic exam patterns.

Pipeline: for each request in REQUEST_SET → POST /api/french/generate-questions
→ judge the markdown output with a strong model against a 6-dim rubric → 0-5
scores + rationale. Aggregates mean per dimension and overall.

Run (API must be up on :8000, .env exported for OPENROUTER_API_KEY):
  set -a && . ./.env && set +a && \
    UV_CACHE_DIR=/tmp/uv-cache uv run --project apps/api \
    python apps/api/scripts/eval_question_gen.py
Flags: --host, --judge-model, --label (tag the run), --only <id>
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "apps/api"))
from app.config import settings  # noqa: E402
from app.gateway import chat_completion  # noqa: E402

RUNS_DIR = REPO_ROOT / "runs"

# ── Fixed request set: board × mode × grade/level × chapter scope ──────────────
# `mode` is sent as a query param; the endpoint ignores it until implemented,
# so baseline runs still work (mode just won't change current output).
REQUEST_SET: list[dict] = [
    {"id": "cbse9_exam", "board": "cbse", "mode": "exam_paper", "difficulty": "A1",
     "chapter": None, "count": 12, "grade": "9",
     "intent": "Full CBSE Class 9 (A1) board-style French paper."},
    {"id": "cbse10_exam", "board": "cbse", "mode": "exam_paper", "difficulty": "A2",
     "chapter": None, "count": 12, "grade": "10",
     "intent": "Full CBSE Class 10 (A2) board-style French paper."},
    {"id": "cbse10_practice_media", "board": "cbse", "mode": "practice_set", "difficulty": "A2",
     "chapter": "Leçon 5", "count": 8, "grade": "10", "question_types": ["fill_in", "short"],
     "intent": "CBSE 10 practice set scoped to Leçon 5 (Les médias)."},
    {"id": "cbse9_practice_achats", "board": "cbse", "mode": "practice_set", "difficulty": "A1",
     "chapter": "Leçon 8", "count": 8, "grade": "9", "question_types": ["mcq", "vrai_faux"],
     "intent": "CBSE 9 practice set scoped to Leçon 8 (Faire des achats)."},
    {"id": "ib_exam_partage", "board": "ib", "mode": "exam_paper", "difficulty": "B1-B2",
     "chapter": "5A", "count": 6, "grade": "12",
     "intent": "IB DP French B exam-style tasks on Partage de la planète 5A."},
    {"id": "ib_practice_media", "board": "ib", "mode": "practice_set", "difficulty": "B1-B2",
     "chapter": "8A", "count": 6, "grade": "11", "question_types": ["short", "mcq"],
     "intent": "IB practice set on Ingéniosité 8A (Communication et média)."},
]

# Compact board-format reference embedded in the judge prompt so it can score
# format_match without guessing. Derived from official CBSE SQP + IB B exam specs.
BOARD_REFERENCE = """
CBSE (Class 9 = A1, Class 10 = A2) — board paper is 80 marks, 4 sections:
- Section A (Compréhension) 10: a French passage, then short-answer Qs (e.g. 2 au choix, 2X2=4),
  "Dites vrai ou faux" (6X0.5=3), "Trouvez dans le texte" word-hunt (3X1=3, e.g. find a preposition,
  a verb form, a synonym, an opposite).
- Section B (Expression écrite) 20: "Ecrivez UNE lettre de 80 mots" (3 choices 2A/2B/2C, 10),
  then 2-of-3 tasks (invitation / dialogue-ordering / cloze) 5X2=10.
- Section C (Grammaire) 30: Conjuguez au temps qui convient; Trouvez la question; Mettez au négatif;
  style direct/indirect; adjectifs/pronoms démonstratifs & possessifs; pronoms relatifs/personnels;
  subjonctif. Each block 5X1=5, usually "5 au choix" and OU alternatives.
- Section D (Culture et Civilisation) 20: "Répondez (20 à 30 mots)" 5X2=10; word-bank cloze 5X1=5;
  matching (colonne A/B) OU vrai/faux 5X1=5.
Instructions are in French (some English glosses). CBSE 9 is simpler (present, passé composé, articles,
30-80 word writing); CBSE 10 adds futur, conditionnel, subjonctif, style indirect, 80-100 word writing.

IB DP French B (B1 SL / B2 HL) — NOT sectioned like CBSE. Authentic tasks:
- Paper 1 (productive): 3 themed task choices, pick ONE, 450-600 words, register-specific text type
  (informal: blog/email/diary; professional: report/proposal/formal letter; mass-media: article/speech/opinion).
- Paper 2 (receptive): reading+listening Qs — MCQ, vrai/faux + justify with text, synonym/antonym,
  matching, short answers.
- Individual oral: SL describe a visual image; HL analyse a literary extract; then themed discussion.
Instructions entirely in French; tasks are integrated/analytical, not isolated drills.
"""

RUBRIC = """Score each dimension 0-5 (5=excellent, 0=absent/wrong). Integers only.
1. format_match: does the output match the board's real exam/task FORMAT for the requested mode?
   exam_paper → sectioned, mark-weighted, board-authentic question types & "au choix" optionality
   (CBSE) or authentic Paper-1/2/oral task shapes (IB). practice_set → a focused list of
   board-authentic question types (not a full paper). Penalise generic "1. question (ref)" lists.
2. grounding: are questions/answers grounded in the provided textbook content (no invented facts,
   no off-corpus references)? Penalise hallucinated passages/answers.
3. level_fit: difficulty appropriate to the level (CBSE9=A1, CBSE10=A2, IB=B1-B2)? Penalise
   too-easy IB or too-hard CBSE 9.
4. answer_key: is there a correct, defensible answer key / mark scheme, and are the answers right?
5. chapter_scope: if a chapter/unit was requested, do questions stay within it? (If no chapter
   requested, score 5 unless it wanders incoherently.)
6. authenticity: instruction phrasing & language authentic to the board (French phrasing for CBSE
   sections / IB tasks; correct task verbs like "Conjuguez", "Trouvez dans le texte", "Reliez",
   "Faites une présentation")?
"""

JUDGE_SCHEMA_HINT = """Return ONLY a JSON object, no prose:
{"format_match":int,"grounding":int,"level_fit":int,"answer_key":int,
 "chapter_scope":int,"authenticity":int,"overall":int,"notes":"<=40 words, key weakness"}"""


async def gen_one(client: httpx.AsyncClient, host: str, key: str, req: dict) -> dict:
    params = {"mode_gen": req.get("mode", "")}  # harmless extra; real mode added later
    body = {
        "board": req["board"],
        "chapter": req.get("chapter"),
        "count": req.get("count", 10),
        "difficulty": req.get("difficulty"),
        "question_types": req.get("question_types"),
        "language_mode": "bilingual",
    }
    # forward mode + grade once the endpoint supports them
    if req.get("mode"):
        body["mode"] = req["mode"]
    if req.get("grade"):
        body["grade"] = req["grade"]
    if req.get("teacher_notes"):
        body["teacher_notes"] = req["teacher_notes"]
    if req.get("gen_model"):
        body["gen_model"] = req["gen_model"]
    t0 = time.perf_counter()
    r = await client.post(
        f"{host}/api/french/generate-questions",
        params={k: v for k, v in params.items() if v},
        headers={"Content-Type": "application/json", "X-OpenRouter-Key": key},
        json=body,
        timeout=180.0,
    )
    r.raise_for_status()
    data = r.json()
    return {
        "markdown": data.get("questions_markdown", ""),
        "chunks_used": data.get("chunks_used", []),
        "gen_ms": int((time.perf_counter() - t0) * 1000),
    }


async def judge_one(key: str, judge_model: str, req: dict, gen: dict) -> dict:
    context_refs = "\n".join(
        f"- {c.get('section_ref')}" for c in gen.get("chunks_used", [])[:15]
    )
    prompt = f"""You are a strict examiner auditing AI-generated French exam questions.

BOARD FORMAT REFERENCE:
{BOARD_REFERENCE}

REQUEST: board={req['board']} grade={req.get('grade')} mode={req.get('mode')} \
level={req.get('difficulty')} chapter={req.get('chapter')} \
types={req.get('question_types')} intent="{req['intent']}"

The generator was given these source section refs (questions should ground in them):
{context_refs or '(none reported)'}

RUBRIC:
{RUBRIC}

GENERATED OUTPUT TO SCORE:
<<<
{gen['markdown'][:6000]}
>>>

{JUDGE_SCHEMA_HINT}"""
    result = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=judge_model,
        openrouter_key=key,
        max_tokens=400,
        temperature=0.0,
    )
    text = (result.get("text") or "").strip()
    # tolerant JSON extraction
    start, end = text.find("{"), text.rfind("}")
    try:
        scores = json.loads(text[start:end + 1])
    except Exception:
        scores = {"error": "judge parse failed", "raw": text[:200]}
    return scores


async def run(host: str, judge_model: str, only: str | None, label: str,
              gen_model: str | None) -> None:
    key = settings.openrouter_api_key
    if not key:
        sys.exit("OPENROUTER_API_KEY not set")
    reqs = [r for r in REQUEST_SET if (not only or r["id"] == only)]
    if gen_model:
        for r in reqs:
            r["gen_model"] = gen_model
    print(f"gen_model={gen_model or 'endpoint default'}  judge={judge_model}")
    rows = []
    sem = asyncio.Semaphore(3)  # gentle on free-tier rate limits

    async def _guarded(coro_fn):
        async with sem:
            return await coro_fn()

    async with httpx.AsyncClient() as client:
        # generate (capped concurrency), then judge
        gens = await asyncio.gather(
            *(_guarded(lambda r=r: gen_one(client, host, key, r)) for r in reqs),
            return_exceptions=True,
        )
    judged = await asyncio.gather(
        *(
            judge_one(key, judge_model, r, g)
            for r, g in zip(reqs, gens)
            if not isinstance(g, Exception)
        ),
        return_exceptions=True,
    )

    dims = ["format_match", "grounding", "level_fit", "answer_key", "chapter_scope", "authenticity", "overall"]
    sums = {d: 0 for d in dims}
    n_ok = 0
    ji = 0
    for r, g in zip(reqs, gens):
        if isinstance(g, Exception):
            print(f"[{r['id']:<22}] GEN ERROR: {g}")
            rows.append({"id": r["id"], "error": f"gen: {g}"})
            continue
        s = judged[ji]; ji += 1
        if isinstance(s, Exception) or "error" in s:
            print(f"[{r['id']:<22}] JUDGE ERROR: {s}")
            rows.append({"id": r["id"], "error": f"judge: {s}", "markdown_head": g["markdown"][:200]})
            continue
        n_ok += 1
        for d in dims:
            sums[d] += int(s.get(d, 0))
        line = " ".join(f"{d[:4]}={s.get(d,'?')}" for d in dims)
        print(f"[{r['id']:<22}] {line}  | {s.get('notes','')[:60]}")
        rows.append({"id": r["id"], "request": r, "scores": s, "gen_ms": g["gen_ms"],
                     "markdown": g["markdown"]})

    print("\n=== AVERAGES" + (f" [{label}]" if label else "") + f"  (n={n_ok}) ===")
    if n_ok:
        for d in dims:
            print(f"  {d:<14} {sums[d]/n_ok:.2f}")

    RUNS_DIR.mkdir(exist_ok=True)
    out = RUNS_DIR / f"qgen-eval-{label or 'run'}-{int(time.perf_counter()*1000)}.jsonl"
    with open(out, "w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"\nWrote {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", default="http://localhost:8000")
    p.add_argument("--judge-model", default="anthropic/claude-sonnet-4-5")
    p.add_argument("--gen-model", default=None, help="override generation model for all requests")
    p.add_argument("--only", default=None, help="run a single request id")
    p.add_argument("--label", default="", help="tag for this run (e.g. baseline, loop1)")
    args = p.parse_args()
    asyncio.run(run(args.host, args.judge_model, args.only, args.label, args.gen_model))


if __name__ == "__main__":
    main()
