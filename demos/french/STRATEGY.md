# French Bot — Quality Strategy & Iteration Notes

## Audience

| Persona | Use case | What they need |
|---|---|---|
| **Student (CBSE 9–10)** | Revise chapters, grammar drills, vocab lookup | A1–A2 examples, atomic exercise blocks, citations to specific Leçon |
| **Student (IB DP 11–12)** | Theme exploration, exam prep, literary analysis | B1–B2 register, Production écrite, Compréhension orale prompts |
| **Teacher** | Lesson plan generation, question banks, exam prep, syllabus mapping | Structured output: objectives + vocab + exercises + answer keys, chapter outlines, theme cross-references |

## Rubric (10-question eval, 5 dims weighted)

| Dimension | Weight | Pass criterion |
|---|---|---|
| Retrieval relevance | 30% | Expected `doc_id` substring in retrieved chunks |
| Keyword coverage | 30% | Topic vocab appears in retrieved content |
| Refusal correctness | 20% | Does NOT refuse when relevant chunks exist |
| Grounded answer | 10% | Cites at least one retrieved `section_ref` |
| Latency | 10% | < 30s end-to-end |

Eval harness: `golden_sets/_french_eval_iter.py`.

## Iteration log

| Iter | Change | Avg score | Wrong refusals |
|---|---|---|---|
| 1 (baseline) | Existing chunking + prompt | 0.71 | 2/10 |
| 2 | Relaxed refusal rule, student/teacher modes | 0.73 | 1/10 |
| 3 | top_k 20→40, top_n 5→8 | **0.83** | **0/10** |

### Per-query trajectory (selected)

| Question | Iter 1 | Iter 3 | Notes |
|---|---|---|---|
| Q3 doctor visit | 0.52 | 0.82 | Bigger top_k surfaced "Nargis chez le médecin" |
| Q5 education system | 0.45 | 0.75 | Relaxed refusal + bigger top_k |
| Q6 unemployment | 0.46 | 0.76 | Refusal heuristic fixed |
| Q4 political system | 0.78 | 0.94 | More candidates → better rerank |
| Q8 chapter 6 (filter) | 0.60 | 0.70 | Hard SQL chapter filter (eval scoring needs work) |

## Implemented fixes

1. **Chapter-number filter** (`apps/api/app/query.py` + `retrieval.py`) — regex-detect `(Leçon|Chapter|Chapitre|Lesson)\s+(\d+)` in user query → hard SQL filter `section_ref ILIKE '%Leçon N%'`.
2. **Cross-vocab aliases at embed time** (`demos/french/ingest_french.py:_aliases_for_section`) — append `Chapter N | Lesson N | Class 10 | Grade 10 | 10th grade` to contextual header so BM25 + dense both find chunks regardless of query phrasing.
3. **Admin/preamble skip** — drop Article 51A, Preface, Hindi Constitution preamble, Table des matières, CBSE Advisors. CBSE chunks: 733 → 497 (32% noise eliminated).
4. **Atomic blocks preserved** — À TOI, Activity, Questions de compréhension, Test, Objectifs, Bilan, Recherche, Épreuve orale kept whole, never split mid-block.
5. **Inherited Leçon numbers** — when marker OCR drops the number on some `# LEÇON` headings, parser inherits from preceding numbered Leçon (running counter).
6. **Sanitized BM25 query** — strip Lucene-special chars so French apostrophes don't crash parser.
7. **Relaxed refusal rule** — bot now answers with caveats when chunks are tangentially relevant instead of refusing.
8. **Student/teacher mode in prompt** — bot switches to structured output (objectives + vocab + exercises + keys) when query is teacher-framed.
9. **Cohere Rerank v3.5** swapped in (Nemotron free was timing out) — reliable refusal + better order.
10. **DeepSeek V3.2 + GLM 4.7 Flash HyDE** for stronger French generation.

## Remaining gaps

| Gap | Severity | Plan |
|---|---|---|
| Reranker still occasionally promotes grammar-example chunks containing topic vocab (e.g., "médecin" as example noun) above content chunks | Medium | Add chunk-type tag in `metadata` (grammar / vocab / dialogue / culture / exercise) → rerank with type-aware boosts. |
| `top_k=40 top_n=8` works in eval but UI sends defaults (`top_k=20 top_n=5`) | Medium | Update `apps/web/lib/api.ts` to use `top_k=40 top_n=8` for french demo. |
| No lesson-plan templates in corpus | Low | Teacher prompts produce plans from chunks; could ingest sample plans later. |
| Pedagogical metadata not tagged | Medium | Tag chunks: `level` (A1/A2/B1/B2), `skill` (grammar/vocab/listening/reading/writing/speaking), `topic` (family/health/environment/…). |
| Answer keys redacted by Rule 4 may frustrate teachers | Low | Move answer-key lookup behind `mode=teacher` query flag (auth-gated in production). |
| Reranker chunks all retrieved at same score for ambiguous queries → stochastic order | Low | Add Phase 2 contextual embeddings (LLM blurb) for short/dense chunks. |

## Strategy — next 5 iterations (proposed)

### Iter 4 — Chunk-type tagging
- Tag each chunk during ingest: `type` ∈ {grammar, vocab, dialogue, exercise, culture, theme_intro, summary}.
- Use heading text + content heuristics (e.g., À TOI = exercise, J'observe = grammar, Lis le texte = dialogue).
- Surface in `metadata` JSON for retrieval boosting + UI filtering.

### Iter 5 — Pedagogical level + skill metadata
- Per-doc: `level: A1/A2/B1/B2`, derived from doc_id (CBSE_9/10 → A1/A2; IB_DP → B1-B2).
- Per-chunk: `skill: reading/writing/listening/speaking/grammar/vocab` from heading text.
- Eval queries: tag expected level + skill. Score retrieval on level+skill match.

### Iter 6 — Lesson plan template
- Add `mode=lesson_plan` URL param.
- Prompt template: produce a 45-min lesson plan with sections (warm-up, presentation, practice, assessment, homework) using only retrieved chunks.
- Output downloadable as Markdown/PDF.

### Iter 7 — Teacher dashboard view
- New page `/french/teacher` — chapter outline tree, expandable per Leçon.
- Pulls all chunks for a Leçon, groups by chunk-type tag.
- Search + filter by skill/level.

### Iter 8 — Question generator
- Dedicated `/french/generate-questions` flow.
- Inputs: chapter, count (5/10/20), difficulty (A1-B2), question types (MCQ, fill-in, short, essay).
- Output: questions + answer key, source-cited.

## Architecture decisions (stable)

- **bge-m3 1024-d embedder** — locked, multilingual, asymmetric retrieval
- **DeepSeek V3.2 generator** — best French quality/cost on OpenRouter
- **Cohere Rerank v3.5** — multilingual, reliable refusal
- **GLM 4.7 Flash HyDE** — cheap hypothetical doc gen
- **Chunking**: markdown-header tree + atomic-block protection + paragraph-pack with sentence fallback, 400 token target
- **Contextual headers** at embed time (Phase 1 of Anthropic Contextual Retrieval)
- **Board filter** as orthogonal scope (CBSE / IB / All) via `metadata->>'board'`
- **Chapter filter** as automatic SQL `ILIKE` when user names a number

## Cost model (per query)

| Component | Avg tokens | $/M | $/query |
|---|---|---|---|
| Embed query | ~10 | $0.01 | ~$0 |
| Rerank | top_k chunks | $0.001/search | $0.001 |
| Generate (DeepSeek V3.2) | ~1500 in, ~800 out | $0.23 / $0.34 | ~$0.0007 |
| HyDE (only on hyde mode) | ~256 out | $0.40 | ~$0.0001 |
| **Total per query** | | | **~$0.002** |

Sustainable cost. Bulk ingest one-time: $2.10 (already spent for current corpus).
