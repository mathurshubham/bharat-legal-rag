# Next Steps — French RAG / Teacher Question Generator

_Updated 2026-06-29. Branch `main`, head `09d1928`._

## Where we are

**Question generator** rebuilt + validated. Strong-judge (qwen3-235b) score: **overall 4.82/5**,
all dims 4.55–5.0. Two modes (`exam_paper` / `practice_set`), board×grade scoping, chapter
tag-fetch, two-pass exam keys, marking-scheme answer keys, teacher free-text steering.

**Two eval harnesses** (french only):
- `apps/api/scripts/eval_french_retrieval.py` — 56 golden cases, deterministic. Gates:
  candidate_hit@40 ≥0.95, final_hit@8 ≥0.95, MRR ≥0.85, board_leak=0. Currently all 1.0 / 0.
- `apps/api/scripts/eval_question_gen.py` — 11 fixed requests, LLM-judge rubric (6 dims).

**Model choices**: generator `deepseek/deepseek-v3.2` (cheap, reliable). Judge — `deepseek-v3.2`
for fast/cheap day-to-day, a strong judge (`qwen/qwen3-235b-a22b` / `z-ai/glm-4.6` /
`anthropic/claude-sonnet-4-5`) for trustworthy milestone scores. Cheap vs strong judge disagree
by ~0.8 overall; strong judge is right.

## Known residuals (prioritized)

### P1 — IB exam answer keys occasionally thin/truncated
Strong judge's only sub-4.5 hits: `ib_exam_partage` answer_key=3 ("missing Paper 1 rubric +
model"), `ib_exam_identites`=4 ("truncated model in Tâche A").
Fix: in the two-pass key step (`main.py` exam_paper branch / `question_gen.build_key_prompt`),
raise the IB key-pass `max_tokens` (4000→6000) or split the IB key per épreuve (1 / 2 / oral).
Re-eval with a strong judge.

### P2 — Competency-based questions need their own path (CBSE 50% mandate)
CBSE 2025-26 requires ~50% competency items (case/source-based, assertion-reasoning, application).
Bolting it onto the exam prompt (loop C) regressed every dim — produced hybrid papers.
Fix: a separate `competency` sub-mode or a dedicated second section, NOT a global instruction.
Build + eval in isolation.

### P3 — Eval signal quality
Cheap deepseek judge is noisy (overall swings ~3.6–4.5 on identical code) and harsh.
Fix options: (a) default milestone eval to a strong Chinese judge (qwen3-235b/glm-4.6);
(b) average 3 runs/config; (c) make the rubric mode-aware so practice_set isn't penalized for
not being a full sectioned paper (`format_match` undercount).

### P4 — generate-questions latency
Two-pass exam = 2 sequential LLM calls (slow). Acceptable for teacher batch use; if interactive,
stream the paper while the key generates, or parallelize where safe.

## Other open threads (from earlier sessions)

- **Chat `/query` answer-quality eval** — retrieval is gated, but generated *answer* groundedness /
  citation correctness / refusal behavior has no automated eval. Build one (LLM-judge over the
  golden set's expected_answer/assertions).
- **Total query latency 12–48s** — streaming fixed *perceived* latency only; trim prompt context
  / cap max_tokens for real total-latency win (re-run retrieval eval after — touches retrieval).
- **Other demos** (law/health/support/insurance/education) have no golden sets / evals.

## Ops notes

- OpenRouter key runs out of credits fast under eval bursts (403 on `/embeddings` = no balance).
  Strong-judge runs are the main spend. Keep deepseek judge for routine loops.
- Re-ingest (`demos/french/ingest_french.py --purge`) re-embeds all 7 docs; re-run retrieval eval
  after ANY ingest/retrieval/boost change.
- API must run with `--reload` so prompt/code edits go live without restart.

## Suggested order

1. P1 (IB key tokens) — cheap, closes the one real quality gap. Re-eval (strong judge).
2. P3a — make strong judge the milestone default + mode-aware format rubric.
3. P2 — competency sub-mode (real-world value; do it isolated so it can't regress the clean path).
4. Chat answer-quality eval (broadens coverage beyond retrieval + question-gen).
