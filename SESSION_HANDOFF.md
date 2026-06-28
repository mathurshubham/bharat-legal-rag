# French RAG — Session Handoff & Strategy

_Last updated: 2026-06-28 (session 2). Branch `main`, head `4bb4a56`._

## 1. What was just done (committed this session)

**`4cf70a2` — feat: stream LLM generation via SSE.** Generation was 63–91 % of a
22–37 s query (NOT condense, as the prior handoff guessed — see §2). Streaming
turns the blocking wait into ~2 s to sources, ~5 s to first token.
- `apps/api/app/gateway.py` — `chat_completion_stream` over OpenRouter SSE
  (`stream:true` + `stream_options.include_usage`).
- `apps/api/app/query.py` — extracted shared `_prepare_generation` pipeline; added
  `POST /api/{demo}/query/stream` (SSE: `meta` → `delta`×N → `done`). Non-streaming
  `/query` kept for backward compat + eval.
- `apps/web/lib/api.ts` — `postQueryStream` (fetch + ReadableStream SSE parser).
- `apps/web/app/[demo]/page.tsx` — `send()` appends deltas live.

**`4bb4a56` — fix: per-Leçon CBSE chapter tagging + recover unindexed Leçons 1-6.**
Two bugs, both in `demos/french/ingest_french.py`:
- CBSE 9 Leçons 1-6 (~half the book) were never indexed. The L1 book-title
  heading "Entre Jeunes" was flagged admin and, in the flat OCR heading structure,
  subtree-skipped all lesson content nested under it. Fix: dropped
  `^Entre Jeunes$` / `^EJ-N` from `ADMIN_HEADING_PATTERNS`. CBSE 9: 189 → 370 chunks.
- Leçon tags were garbage (a counter matched stray "Leçon N" refs in the grammar
  appendix → 67/149-chunk lumps). Fix: count end-of-lesson recap markers
  ("Je révise ce que je viens d'apprendre", exactly 12 per doc) → running lesson
  number, mapped to titles from the SOMMAIRE (`_CBSE_LESSON_TITLES`). Title now in
  section_ref, contextual header, and aliases.
- `golden_sets/french-v2-dataset.csv` — IB cases 10 → 25; fixed 1 stale CBSE
  negation expectation.

## 2. Corrected findings (prior handoff was wrong on these)

- **Latency bottleneck is GENERATION, not condense.** Measured per-stage: single-turn
  condense=0 (auto-skipped, no history), retrieve≈2 s, rerank≈1 s, generate=12–48 s.
  Condense adds only ~4 s on multi-turn. Streaming was the right P1, not condense-skip.
- **CBSE source has no per-Leçon body anchors** — no lesson headings, no page markers,
  no images; titles live only in the SOMMAIRE. Per-Leçon segmentation was thought
  infeasible, but the per-lesson recap marker ("viens d'apprendre", 12× per doc)
  turned out to be a reliable anchor. Unit-level fallback was NOT needed.

## 3. Measured state — v2 retrieval eval (56 cases)

Re-run after full re-ingest. DB: **2794 chunks / 7 docs** (was 2612; +182 = CBSE 9
recovery).

| metric | value | was (41 cases) |
|---|---|---|
| candidate_hit@40 | 1.000 | 1.000 |
| final_hit@8 | 1.000 | 1.000 |
| MRR | 1.000 | 0.927 |
| type_hit@8 | 0.885 | 0.919 |
| chapter_hit@8 | 1.000 | 0.946 |
| board_leak | 0 | 0 |

Per-board: **IB 25 cases — final_hit@8=1.0, MRR=1.0, type=0.96, chapter=1.0** (verified,
no longer undersampled). CBSE 28 cases — final=1.0, MRR=0.981, type=0.821, chapter=1.0.

## 4. How to resume the stack

```bash
docker ps | grep legal-rag-db        # :5435 -> 5432

# API — WITH --reload (so SSE/code edits go live)
cd apps/api && set -a && . ../../.env && set +a && \
  nohup uv run uvicorn app.main:app --port 8000 --reload > /tmp/legal-rag-api.log 2>&1 &
curl -sf http://localhost:8000/api/health     # {"status":"ok"}

cd apps/web && pnpm dev                        # :3002

# Retrieval eval
set -a && . ./.env && set +a && \
  UV_CACHE_DIR=/tmp/uv-cache uv run --project apps/api \
  python apps/api/scripts/eval_french_retrieval.py
# Re-ingest (re-embeds all 7 docs): demos/french/ingest_french.py --purge
```

UI e2e via `agent-browser` (docs: `agent-browser-docs.md`). Web reads the OpenRouter
key from localStorage blob `rag-demo-settings` = `{"openrouterKey":"sk-or-..."}`.

Streaming SSE smoke test:
```bash
curl -sN -X POST "http://localhost:8000/api/french/query/stream?mode=hybrid" \
  -H "Content-Type: application/json" -d '{"q":"Explique le passé composé"}'
```

## 5. Known residual issues

1. **type_hit@8 = 0.885** (not gated). CBSE vocab/culture/edge cases where the top
   chunk's `metadata.type` doesn't intersect expected_types. Borderline; not chased
   (chasing risks overfitting the classifier to the eval).
2. **Total generation latency still 12–48 s.** Streaming fixed *perceived* latency
   only. Open lever: trim prompt context (5475 prompt tokens at top_n=8) and/or cap
   `max_tokens`. Must re-run eval (touches retrieval surface).
3. **generate-questions chapter scope leaks** (`apps/api/app/main.py:219`) — a Leçon 5
   request still pulls some other-Leçon chunks. Now that Leçon tags are correct, a
   hard chapter filter is finally viable.
4. **condense null** only patched, not root-caused (`condense.py` — cheap model
   sometimes returns null). Log null-rate / consider model swap.

## 6. Next course of action (prioritized)

- **P-A — generate-questions hard chapter filter** (`main.py:219`). Now unblocked by
  correct Leçon tags. Filter to chapter chunks when ≥N exist; fall back to boost.
- **P-B — prompt-context trim + max_tokens cap.** Real total-latency lever. Re-eval after.
- **P-C — teacher UX**: lesson-plan / question-bank PDF export, saved banks.
- **P-D — type classifier** improvement if type_hit matters for a feature.

## 7. Eval gates to hold (regression guard)
- candidate_hit@40 ≥ 0.95, final_hit@8 ≥ 0.95, MRR ≥ 0.85, board_leak = 0.
- Re-run `eval_french_retrieval.py` after ANY ingest or retrieval/rerank/boost change.
- Keep serving (`query.py`) and eval harness rerank-window logic in sync.
- After any ingest change, re-ingest (`--purge`) before trusting eval numbers.
