# Chunking Strategy — Analysis & Per-Domain Recommendations

This document (1) describes the chunking the platform does **today**, (2) summarizes what the research and open-source ecosystem say works best, and (3) gives **concrete, per-domain recommendations** grounded in each demo's actual corpus and section grammar.

> TL;DR — The current pipeline is **structure-aware then fixed-token**, which is already a strong, defensible baseline. The single highest-leverage upgrade is to **stop embedding "naked" sub-chunks**: prepend each chunk's `doc_title` + `section_ref` (and chapter where available) before embedding, and adopt **parent-document ("small-to-big") retrieval** so the generator always sees a coherent whole section. Reserve semantic/agentic chunking for the demos where an A/B test on the golden set actually shows a win — research repeatedly finds it does *not* beat recursive splitting on most corpora and is ~14× slower.

---

## 1. What the platform does today

From `apps/api/scripts/ingest.py` and each demo's `manifest.yaml`:

```
load_doc()         PDF→text (pypdf) or read clean .txt/.md (marker-pdf output)
   │
segment_text()     Split into SECTIONS using manifest regex patterns.
   │               Picks the pattern with the most matches; each match→next
   │               match becomes one section. Produces a section_ref
   │               (e.g. "BNS s.103", "Art. 21", "CP cl.5").
   │
sub_chunk()        If a section ≤ 512 tokens → 1 chunk.
   │               Else sliding window of CHUNK_TOKENS=512 with
   │               OVERLAP_TOKENS=64 (tiktoken cl100k_base).
   │
embed_doc()        bge-m3, 1024-dim → INSERT into chunks(content, embedding,
                   section_ref, chunk_index, doc_title, visibility, metadata, …)
```

This is a **two-level hierarchy**: a *semantic/structural* split (sections) followed by a *fixed-size* split (token windows). It is meaningfully better than naive fixed-size chunking because boundaries mostly fall on real statutory/topical units.

### Strengths
- **Structure-aware boundaries.** Sections, Articles, Clauses, and headings are first-class — the right unit for statutes, policies, and fact sheets.
- **Stable citations.** Every chunk carries a `section_ref`, which powers grounded citations and the validation oracle.
- **Token-accurate sizing.** `tiktoken` gives exact budgets (no surprise truncation at the embedder).
- **Per-demo grammar.** Each domain supplies its own regex patterns and citation format — clean separation.

### Weaknesses (the upgrade targets)
1. **Naked sub-chunks lose their heading.** A section's heading text only lives in `chunk_index = 0`. Every *subsequent* window (`chunk_index ≥ 1`) is embedded with **no indication of which section/Act it belongs to**. The `section_ref` is stored as a column but is **not part of the embedded text** — so the vector for "…shall be punished with imprisonment…" doesn't know it's BNS s.103. This is exactly the failure mode contextual retrieval targets (see [contextual-embeddings.md](contextual-embeddings.md)).
2. **Token-window slicing cuts mid-sentence/mid-clause.** `sub_chunk()` slices on token offsets, not sentence/paragraph boundaries, so a window can begin mid-sentence or split a clause from its proviso. The 64-token overlap softens but doesn't fix this.
3. **No table/list protection.** A Markdown table or a numbered list of exclusions can be sliced across two chunks, destroying its meaning (acute for insurance benefit tables and health dosage lists).
4. **Retrieve-granularity == generate-granularity.** Whatever 512-token window is retrieved is what the LLM sees. For statutes the natural reading unit is the **whole section**; retrieving one window of a long section gives the model a partial provision.
5. **`cl100k_base` under-segments non-English text.** For the French demo the token budget is skewed (accented/agglutinative tokens), so "512 tokens" is a different amount of content than in English.

---

## 2. What the research & ecosystem say

### 2.1 The headline finding: recursive/structural is a hard-to-beat baseline
Multiple 2024–2026 evaluations converge on the same conclusion: **recursive, structure-respecting splitting around ~512 tokens is the best default**, and "smarter" semantic chunking rarely justifies its cost.

- A 2026 cross-strategy benchmark placed **recursive 512-token splitting first (~69% accuracy)** with semantic chunking well behind (~54%), the latter producing tiny ~43-token fragments. ([firecrawl](https://www.firecrawl.dev/blog/best-chunking-strategies-rag), [buildmvpfast](https://www.buildmvpfast.com/blog/chunking-strategies-rag-semantic-fixed-size-recursive-2026))
- **"Is Semantic Chunking Worth the Computational Cost?"** finds semantic chunking's gains are inconsistent and often unjustified versus simpler splitting — and it runs **~14× slower** (0.33 vs 4.82 MB/s). ([arXiv:2410.13070](https://arxiv.org/abs/2410.13070))
- A January 2026 analysis identified a **"context cliff" around ~2,500 tokens** where answer quality drops, and found **sentence chunking matches semantic up to ~5,000 tokens** at a fraction of the cost. ([langcopilot](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide))
- Production guidance from vector-DB vendors echoes this: **start with recursive character chunking**; only reach for semantic/agentic methods if an A/B test on *your* corpus shows a win. ([Redis](https://redis.io/blog/chunking-strategy-rag-pipelines/), [Weaviate](https://weaviate.io/blog/chunking-strategies-for-rag))

**Caveat:** in **highly structured / safety-critical** domains, *adaptive* chunking aligned to logical topic boundaries can win big — a clinical-decision-support study reported **87% vs 13%** for fixed-size baselines. The lesson isn't "semantic > recursive"; it's "**respect the document's real structure**," which the platform already does. ([NCBI PMC12649634](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12649634/))

### 2.2 Techniques worth adopting (in rough order of ROI here)

| Technique | Idea | When it helps | Library / source |
|-----------|------|---------------|------------------|
| **Contextual headers** | Prepend doc title + section path to each chunk before embedding | Always; biggest win on structured corpora | (see [contextual-embeddings.md](contextual-embeddings.md)) |
| **Parent-document / small-to-big** | Index small child chunks; return the parent section to the LLM | Statutes, policies — when the reading unit > retrieval unit | [LlamaIndex AutoMerging/ParentDocument](https://docs.llamaindex.ai/), [LangChain ParentDocumentRetriever](https://python.langchain.com/docs/how_to/parent_document_retriever/) |
| **Structure/Markdown-header splitting** | Split on `#`/`##`/heading hierarchy, carry the header path as metadata | Markdown KBs, textbooks | [LangChain MarkdownHeaderTextSplitter](https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/) |
| **Layout/table-aware extraction** | Keep tables, lists, and figures as atomic units | Insurance benefit tables, schedules | [Unstructured](https://docs.unstructured.io/), [Docling](https://github.com/docling-project/docling) |
| **Summary-Augmented Chunking (SAC)** | Attach a document-level synthetic summary to each chunk for global context | Long, cross-referential docs (legal) | [arXiv:2510.06999](https://arxiv.org/abs/2510.06999) |
| **Late chunking** | Embed the whole doc, then pool token vectors into chunks — context without an LLM call | Long docs; cheap contextualization | [arXiv:2409.04701](https://arxiv.org/abs/2409.04701) |
| **Proposition / "Dense X" chunking** | LLM rewrites text into atomic self-contained facts, embed those | Fact-dense lookup (health, FAQ); costly | Dense X Retrieval (Chen et al., 2023) [arXiv:2312.06648](https://arxiv.org/abs/2312.06648) |
| **Hierarchical (RAPTOR)** | Recursively cluster + summarize into a tree; retrieve at multiple levels | Cross-document / thematic questions | [RAPTOR, arXiv:2401.18059](https://arxiv.org/abs/2401.18059) |
| **Semantic chunking** | Split where embedding similarity drops | Only if it beats recursive on your eval | [Chonkie](https://github.com/chonkie-inc/chonkie), [LlamaIndex SemanticSplitter](https://docs.llamaindex.ai/) |

### 2.3 Size & overlap rules of thumb
- **Default to ~512 tokens with ~10–15% overlap** (the platform's 512/64 ≈ 12.5% is right in the pocket).
- **Smaller (256–400)** for precise fact/FAQ lookup (support, health bullets).
- **Larger or whole-unit** for documents read as a block (statutory sections, policy clauses) — paired with parent-document retrieval so you don't bloat the index.
- **Never exceed the "context cliff" (~2,500 tokens)** for a single chunk fed to the generator.

---

## 3. Per-domain recommendations

Each demo's current section grammar (from `manifest.yaml`) and the recommended changes:

### 3.1 `law` — Vidhi (Indian statutes) — *highest priority, highest payoff*
**Current grammar:** `^(?:Section\s+)?(\d+[A-Z]?)\.\s`, `^Article\s+…`, `^(Schedule…|PART…)`. Already section/Article-aware. ✅
**The literature strongly endorses statute structure-awareness** ([arXiv:2510.06999](https://arxiv.org/abs/2510.06999), [arXiv:2604.06173](https://arxiv.org/abs/2604.06173), [Graph RAG for Legal Norms arXiv:2505.00039](https://arxiv.org/abs/2505.00039)).

Recommendations:
1. **Contextual section headers on every sub-chunk** — prepend `"{doc_title} — {section_ref}: {section_heading}"`. This fixes weakness #1 and is the top win. (Statutes are the ideal case: the structure *is* the disambiguator.)
2. **Parent-document retrieval** — index 512-token children, but pass the **full section** to the LLM. A user asking about s.103 should get all of s.103, not window 2 of 3.
3. **Preserve sub-structure** — keep sub-section `(1)/(2)`, clauses `(a)/(b)`, **provisos**, and **Explanations** with their parent; never split a proviso from its rule.
4. **Tables & Schedules** — segment Schedules as their own units; keep tabular content intact.
5. **Cross-references as metadata** — when a section cites another ("subject to section 100"), store the referenced refs in `metadata` to enable reference-following / SAC-style global context.
6. Keep the existing repealed-law `LAW_MAPPINGS` crosswalk as a first-class doc (it already is).

### 3.2 `education` — Padhai (NCERT Class 10)
**Current grammar:** `^(\d+\.\d+(?:\.\d+)?)\s+[A-Z]`, `^(Activity\s+\d+|Box\s+\d+)`, `^([A-Z][A-Z ]{3,})$` (ALL-CAPS headings).
Recommendations:
1. **Markdown-header / heading-path chunking** — carry the chapter → section heading path into each chunk's context header (pedagogical breadcrumbs aid retrieval).
2. **Treat Activities/Boxes as atomic chunks** — they're self-contained Q&A/exercise units; don't merge or split them.
3. **Slightly smaller children (~300–450 tokens)** — student questions are usually fact-scoped.
4. **Parent = section, child = paragraph** for "explain this concept" style answers.

### 3.3 `health` — Vaidya (WHO fact sheets)
**Current grammar:** topical headings (`Symptoms`, `Treatment`, `Prevention`, `Causes`, `Diagnosis`, …).
These headings are short and highly meaningful — a strong fit for **header-prefixed, section-whole chunks**.
Recommendations:
1. **Keep each topical section whole** (they're short) and **prefix the disease + heading** (`"Dengue — Symptoms:"`). Big retrieval win for "symptoms of X" queries.
2. **Never split a warning/dosage/qualifier from its statement** — protect lists and cautions (safety).
3. **Proposition chunking is worth an A/B** here — fact sheets are bullet-dense, and atomic facts retrieve cleanly — but measure against the cost.
4. Maintain the strict "general information, not medical advice" framing in the prompt (already present).

### 3.4 `insurance` — Beema (IRDAI policy wordings)
**Current grammar:** `^(?:Clause|Section|Article)\s+(\d+[A-Z]?\.?\d*)`, numbered sub-headings, `^(Annexure…|Schedule…)`.
Policy wordings are clause/definition/exclusion heavy with **tables** (benefit/sub-limit schedules).
Recommendations:
1. **Layout/table-aware extraction** ([Docling](https://github.com/docling-project/docling)/[Unstructured](https://docs.unstructured.io/)) — keep **benefit tables and sub-limit schedules intact** as single chunks; token-slicing them is the worst failure here.
2. **Definitions and Exclusions as atomic chunks** — "what's *not* covered" must never be split from its clause.
3. **Parent-document retrieval** for cross-referenced clauses ("subject to the waiting period in Clause 4.2").
4. Contextual header = `"{policy} — {clause_ref}: {clause_title}"`.

### 3.5 `support` — Acme Tasks (Markdown KB)
**Current grammar:** `^##\s+(.+)$`, `^###\s+(.+)$` (Markdown headers).
Already heading-aware. Recommendations:
1. **MarkdownHeaderTextSplitter-style hierarchy** — child chunk per `###`, carrying the `H1 > H2 > H3` path as context. ([LangChain](https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/))
2. **Small chunks (~256–400)** — KB lookups are precise; FAQ Q&A pairs should stay atomic.
3. **Respect `visibility`** — internal policies / competitor battlecards are already access-controlled; keep chunking from blurring a confidential paragraph into a public one.

### 3.6 `french` — Bonjour (multilingual study)
**Current grammar:** `^(Unité\s+\d+)`, `^(Leçon\s+\d+)`, `^(Bilan…)`, `^(Thème\s+\d+)`, plus accented heading lines.
Recommendations:
1. **Use a multilingual-aware tokenizer/sentence splitter for sizing**, not `cl100k_base`, which over-counts accented French tokens and skews the 512 budget. (`bge-m3`'s own tokenizer or a sentence-based splitter is more faithful.)
2. **Normalize Unicode (NFC) and accents** at ingest so `é`/`è`/`ê` don't fragment retrieval.
3. **Keep bilingual glossary pairs together** (FR term ↔ EN gloss) so `bilingual` answer mode has both sides.
4. `bge-m3` is already multilingual — no embedding change needed; the work is in segmentation and normalization.

---

## 4. Concrete change list for this repo (prioritized)

These map directly onto `apps/api/scripts/ingest.py` and `init.sql`.

1. **[P0] Contextual chunk headers.** In `ingest_doc()`, build `header = f"[{doc_title} — {section_ref}]"` (extend with chapter/heading) and embed `header + "\n\n" + chunk_text`. Store the **original** in `content` (for display/citations) and the **contextual** text in a new `content_ctx` column used for embedding + BM25. *Zero LLM cost, biggest single recall win.* (Shared with [contextual-embeddings.md](contextual-embeddings.md) §2.2.)
2. **[P0] Sentence/paragraph-aware sub-chunking.** Replace raw token-window slicing in `sub_chunk()` with a recursive splitter that prefers paragraph → sentence boundaries within the 512/64 budget (don't cut mid-clause).
3. **[P1] Parent-document retrieval.** Add `parent_ref`/`parent_id` to `chunks`; retrieve on children, then expand to the full parent section before building the generator context in `query.py:_build_context()`.
4. **[P1] Table/list protection.** Detect Markdown tables/lists during segmentation and emit them as atomic chunks (skip token-window splitting for those).
5. **[P2] Per-demo chunk sizing.** Move `CHUNK_TOKENS`/`OVERLAP_TOKENS` into `manifest.yaml` so support/health can use ~300 while statutes use whole-section + parent.
6. **[P2] Multilingual sizing for `french`.** Swap the tokenizer used for sizing on that demo.
7. **[P3] Optional SAC / late chunking / proposition** — only behind an eval gate (see below).

---

## 5. How to decide (don't guess — measure)

Every change above should be validated with the existing evaluation assets (`golden_sets/`, `validate_sections.py`) before/after. Minimum bar:

- **Retrieval recall@20** — is the gold `section_ref` in the candidate set? (matches Anthropic's failure-rate metric)
- **nDCG@5 after rerank** — are the right chunks on top?
- **Citation precision/recall** — does `citations[]` contain the `expected_citations`?
- **Refusal/guard correctness** — do `refusal`/`guard` cases still behave?

Run the ladder per demo: **baseline → +headers → +sentence-aware → +parent-doc → (only if it wins) +semantic/proposition.** Adopt a technique only where it beats the previous rung on *that* domain. The research is clear that the fancy methods often *don't* — so let the golden set decide. See **[evals-strategy.md](evals-strategy.md)** for the harness.

---

## Sources

- [Anthropic — Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [Is Semantic Chunking Worth the Computational Cost? (arXiv:2410.13070)](https://arxiv.org/abs/2410.13070)
- [Late Chunking: Contextual Chunk Embeddings (arXiv:2409.04701)](https://arxiv.org/abs/2409.04701)
- [Towards Reliable Retrieval in RAG Systems for Large Legal Datasets (arXiv:2510.06999)](https://arxiv.org/abs/2510.06999)
- [Beyond Case Law: Structure-Aware Retrieval for Statute-Centric Legal QA (arXiv:2604.06173)](https://arxiv.org/abs/2604.06173)
- [Graph RAG for Legal Norms: A Hierarchical and Temporal Approach (arXiv:2505.00039)](https://arxiv.org/abs/2505.00039)
- [Bridging Legal Knowledge and AI: RAG with Vector Stores, KGs, and HNMFk (arXiv:2502.20364)](https://arxiv.org/abs/2502.20364)
- [Mix-of-Granularity: Optimize Chunking Granularity for RAG (arXiv:2406.00456)](https://arxiv.org/abs/2406.00456)
- [Dense X Retrieval: What Retrieval Granularity Should We Use? (arXiv:2312.06648)](https://arxiv.org/abs/2312.06648)
- [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval (arXiv:2401.18059)](https://arxiv.org/abs/2401.18059)
- [Comparative Evaluation of Advanced Chunking for Clinical Decision Support (NCBI PMC12649634)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12649634/)
- [Best Chunking Strategies for RAG — Firecrawl](https://www.firecrawl.dev/blog/best-chunking-strategies-rag)
- [Chunking Strategies for RAG Pipelines — Redis](https://redis.io/blog/chunking-strategy-rag-pipelines/)
- [Chunking Strategies to Improve RAG — Weaviate](https://weaviate.io/blog/chunking-strategies-for-rag)
- [Document Chunking for RAG: practical guide — langcopilot](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide)
- [LangChain — MarkdownHeaderTextSplitter](https://python.langchain.com/docs/how_to/markdown_header_metadata_splitter/) · [ParentDocumentRetriever](https://python.langchain.com/docs/how_to/parent_document_retriever/)
- [LlamaIndex — node parsers / auto-merging retriever](https://docs.llamaindex.ai/)
- [Unstructured](https://docs.unstructured.io/) · [Docling](https://github.com/docling-project/docling) · [Chonkie](https://github.com/chonkie-inc/chonkie)
