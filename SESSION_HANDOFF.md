# French RAG — Session Handoff & Strategy

_Last updated: 2026-06-28. Branch `main`, head `9ba37d6`._

## 1. What was just done (committed)

**Commit `9ba37d6` — fix: french topic-term boost + condense null-guard**

- `apps/api/app/query.py`
  - Added `_FRENCH_TOPIC_TERMS`: bilingual trigger→French-term map (media→média/presse/radio, shopping, family, francophonie, food, health, environment, education, travel, work, weather).
  - `_detect_french_intent` now emits `topic_terms`.
  - `_boost_french_chunks` applies a soft, capped additive lexical boost (max 1.5; section/header matches weighted 2× over body). Additive only — no recall loss.
  - Rerank candidate window widened for topic intent (previously grammar-only) so deterministic boosts can recover chunks Cohere down-ranked.
- `apps/api/app/condense.py` — null-guard: `(result.get("text") or "")`, falls back to original query. Fixes a 500 on multi-turn queries when the cheap condense model returns null content.
- `apps/api/scripts/eval_french_retrieval.py` — mirror the rerank-window widen for topic intent (keeps eval == serving).
- `.gitignore` — added `.DS_Store`, `runs/`.

Working tree is clean. `runs/` (eval output jsonl) is gitignored.

## 2. Measured state — v2 retrieval eval (41 cases)

Run: `runs/french-retrieval-1782647232.jsonl`

| metric | value |
|---|---|
| candidate_hit@40 | 1.000 |
| final_hit@8 | 1.000 |
| MRR | 0.927 |
| type_hit@8 | 0.919 |
| chapter_hit@8 | 0.946 |
| board_leak | 0 |

Per-board:

| board | cases | final_hit@8 | MRR | type_hit | chapter_hit | leak |
|---|---|---|---|---|---|---|
| IB | 9 | 1.000 | 1.000 | 1.000 | 1.000 | 0 |
| CBSE | 27 | 1.000 | 0.900 | 0.889 | 0.926 | 0 |

**IB beats CBSE on every metric — but IB is undersampled** (~2115 of 2612 chunks, only 9 eval cases). CBSE is now the weaker board: OCR / chapter-tag noise in Entre Jeunes, especially CBSE 9 running-counter lumping (Leçon 2 = 67 sections all "revision", Leçon 9 = 149 sections).

DB: french re-ingested this session — 2612 chunks / 7 docs. Type labels improved (grammar 34→49) but still skewed (vocab=7, dialogue=1, content=827 unclassified).

## 3. How to resume the stack

```bash
# DB (already up; verify)
docker ps | grep legal-rag-db        # :5435 -> 5432

# API — restart WITH --reload (prior sessions ran without it, so live code was stale)
cd apps/api && set -a && . ../../.env && set +a && \
  nohup uv run uvicorn app.main:app --port 8000 --reload > /tmp/legal-rag-api.log 2>&1 &
curl -sf http://localhost:8000/api/health     # {"status":"ok"}

# Web
cd apps/web && pnpm dev                        # :3002

# Retrieval eval (env must export DATABASE_URL + OPENROUTER_API_KEY)
set -a && . ./.env && set +a && \
  UV_CACHE_DIR=/tmp/uv-cache uv run --project apps/api \
  python apps/api/scripts/eval_french_retrieval.py
# flags: --no-rerank, --category <grammar|vocab|culture|chapter|teacher|edge|refusal>, --mode bm25|vanilla|hybrid|hyde
```

UI e2e via agent-browser (docs: `agent-browser-docs.md`). Web reads the OpenRouter key from localStorage blob `rag-demo-settings` = `{"openrouterKey":"sk-or-..."}` (NOT a bare `openrouterKey` key).

## 4. Known residual issues (none block retrieval gates)

1. **condense null only patched, not root-caused.** Cheap condense model (`hyde_model` slot = glm-4.7-flash) sometimes returns null content. Log the null-return rate; consider swapping the model. `apps/api/app/condense.py:63`.
2. **generate-questions chapter scope leaks.** A "Leçon 5" request still pulls some Leçon 2 chunks — it prioritizes chapter chunks but doesn't filter when enough exist. `apps/api/app/main.py:219`.
3. **Query latency 22–37s.** Full condense→retrieve→rerank→gen chain; condense adds an LLM round-trip on every follow-up.
4. **CBSE 9 chapter tagging imperfect.** Running-counter in `demos/french/ingest_french.py` lumps many chunks under one Leçon. Drags CBSE chapter_hit/type_hit.
5. **IB undersampled in eval** — 9 cases over the largest corpus.

## 5. Next course of action (prioritized)

### Priority 1 — Latency (biggest user-visible win; retrieval already at gates)
- Profile the 22–37s chain (instrument condense/retrieve/rerank/gen ms — already in `latency` response field).
- Skip condense when history is short or query already standalone; cache condense results.
- Consider parallelizing rerank candidate fetch.
- Target: < 10s p50.

### Priority 2 — CBSE 9/10 chapter tagging
- Fix running-counter logic in `demos/french/ingest_french.py` (`chunk_type_of` + Leçon assignment) so chunks map to the correct Leçon instead of lumping.
- Re-ingest CBSE only: `uv run --project apps/api python demos/french/ingest_french.py --doc CBSE_9_ENTREJEUNES --purge` (note: `--purge` deletes ALL french; for single-doc reload without nuking others, ingest without `--purge` after a targeted delete, or re-ingest all 7).
- Re-run eval; expect CBSE chapter_hit/type_hit up.

### Priority 3 — Expand IB eval (verify the perfect score)
- Grow IB cases ~9 → 25 in `golden_sets/french-v2-dataset.csv`:
  - per-theme depth (Identités, Expériences, Ingéniosité, Org sociale, Partage)
  - unit-letter disambiguation (8A vs 8B, 5A vs 6B)
  - resource-PDF content (transcripts, exam papers, oral activities)
  - cross-theme distractors (e.g. média in both IB Ingéniosité 8A and CBSE Leçon 5 — confirm board filter holds)
- Re-run; confirm IB metrics hold under harder coverage.

### Priority 4 — generate-questions scope
- In `apps/api/app/main.py:219`, hard-filter to chapter chunks when ≥N exist; fall back to boost-only when sparse.

### Priority 5 — Teacher UX (Tier 2 features)
- Lesson-plan / question-bank PDF export.
- Saved question banks (lightweight DB table).

## 6. Eval gates to hold (regression guard)
- candidate_hit@40 ≥ 0.95, final_hit@8 ≥ 0.95, MRR ≥ 0.85, board_leak = 0.
- Re-run `eval_french_retrieval.py` after ANY ingest or retrieval/rerank/boost change.
- Keep serving (`query.py`) and eval harness rerank-window logic in sync.
