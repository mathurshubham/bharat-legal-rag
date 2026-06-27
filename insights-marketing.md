# Marketing & Résumé Insights

How to position this project so it lands — on a résumé, on LinkedIn/X, on GitHub, and in interviews. Copy-paste blocks below; replace `[bracketed]` placeholders with real numbers from your eval harness (see [evals-strategy.md](evals-strategy.md)) so claims are credible, not vague.

---

## 1. The one-liner (pick by context)

- **Shortest:** "A production-grade, multi-domain RAG platform with hybrid retrieval, strict citation grounding, and built-in evaluation — running on a Raspberry Pi."
- **Recruiter-friendly:** "I built a RAG engine that answers questions only from a trusted corpus and cites every claim — then proved it works across six domains (law, health, insurance, education, support, French) with a golden-dataset eval harness."
- **Technical:** "One config-driven RAG engine: ParadeDB (pgvector HNSW + BM25) → RRF fusion → cross-encoder rerank → Claude, with refusal/repealed-law guardrails and document-level access control. Adding a domain is a folder, not a fork."

**Why it stands out:** most portfolio RAG projects are "embed PDFs, call an LLM." This one has the things real systems need — **hybrid retrieval, reranking, grounding/refusal, access control, evaluation, and cheap deployment** — which is exactly the gap interviewers probe for.

---

## 2. Naming

| Use | Suggestion |
|-----|-----------|
| Umbrella project | **"Grounded RAG Platform"** or **"Multi-Domain RAG Engine"** |
| Flagship demo (lead with this) | **"Vidhi — Indian Legal RAG"** (concrete, memorable, topical with the 2023 BNS/BNSS/BSA codes) |
| GitHub repo | `grounded-rag` / `rag-demos` / `vidhi-legal-rag` |

Leading with the **legal** demo is smart: the 2023 overhaul of India's criminal codes is current and specific, and "AI that refuses to hallucinate statutes" is a sharp, defensible story.

---

## 3. Résumé

### 3a. Project block (paste-ready)

> **Grounded RAG Platform — Multi-Domain Retrieval-Augmented Generation** &nbsp;·&nbsp; *Personal project* &nbsp;·&nbsp; [github link] · [live demo]
> Config-driven RAG engine serving six grounded assistants (Indian law, health, insurance, education, support, French) from one codebase.
> - Built **hybrid retrieval** (dense `bge-m3`/pgvector-HNSW + BM25) fused with **Reciprocal Rank Fusion** and a **cross-encoder reranker**, raising retrieval recall@20 to **[X]%** over a dense-only baseline.
> - Enforced **strict citation grounding** and an automatic **refusal guardrail**, cutting hallucinated/unsupported citations to **[~0]%** on a [N]-case golden eval set.
> - Designed a **config-only multi-tenant architecture** — a new domain is a manifest + corpus + prompts, **zero core-code changes**.
> - Shipped **document-level access control** (public/internal/confidential) and a **repealed-law guard** mapping superseded statutes (IPC→BNS) to current provisions.
> - Deployed the full stack (FastAPI + Next.js + ParadeDB) on a **Raspberry Pi via Cloudflare Tunnel** with **no GPU at query time**.
> - **Stack:** Python, FastAPI, PostgreSQL/ParadeDB (pgvector + pg_search), Next.js 16/React 19, TypeScript, Docker, OpenRouter (Claude Sonnet 4.5), bge-m3.

### 3b. Single-bullet variants (for a packed résumé)

- *AI/ML focus:* "Built a multi-domain RAG engine — hybrid (dense+BM25) retrieval with RRF fusion and cross-encoder reranking, citation grounding, and a golden-dataset eval harness measuring recall@k, faithfulness, and refusal accuracy."
- *Backend focus:* "Designed a config-driven, multi-tenant FastAPI service over ParadeDB (pgvector HNSW + BM25) with async pooling, per-request retrieval-mode switching, document-level access control, and full per-stage latency tracing."
- *Full-stack focus:* "Shipped an end-to-end RAG product: FastAPI + ParadeDB backend and a Next.js 16/React 19 UI with retrieved-chunk inspector, corpus/dataset viewers, dark mode, and BYO-API-key — deployed on a Raspberry Pi."

### 3c. Skills / keywords (ATS-friendly)
`RAG` · `Retrieval-Augmented Generation` · `Vector Search` · `pgvector` · `HNSW` · `BM25` · `Hybrid Search` · `Reciprocal Rank Fusion` · `Reranking` · `Cross-encoder` · `Embeddings` · `bge-m3` · `Semantic Search` · `LLM` · `Claude` · `HyDE` · `Prompt Engineering` · `LLM Evaluation` · `RAGAS` · `FastAPI` · `PostgreSQL` · `ParadeDB` · `Python` · `Next.js` · `React` · `TypeScript` · `Docker` · `Cloudflare` · `AI Safety / Guardrails`

> **Honesty note:** fill `[X]%`, `[N]`, `[~0]%` with **real numbers** from `scripts/eval.py`. If you haven't run it yet, prefer the unquantified architecture bullets (3b) over invented metrics — interviewers can tell.

---

## 4. Interview talking points (depth that signals seniority)

Each is a 60–90s story showing a real decision, not just a tool name:

1. **"Why hybrid + RRF instead of pure vector search?"** Dense retrieval misses exact statute numbers and rare terms; BM25 nails them but misses paraphrase. RRF fuses both with no score-normalization headache (`1/(K+rank)`, K=60). → shows retrieval-quality reasoning.
2. **"Why ParadeDB / one database?"** pgvector *and* BM25 in a single Postgres means one store, one transaction, filters fused into the index walk — no separate vector DB + search cluster to keep in sync. → shows systems pragmatism.
3. **"How do you stop it hallucinating?"** Grounded prompt (cite only retrieved refs) + canonical refusal + a UI that detects refusal/guard banners + a golden eval that *fails the build* if it answers out-of-corpus questions. → shows you treat safety as testable, not aspirational.
4. **"How is it multi-tenant?"** A demo is pure config (manifest grammar, corpus, prompts, validation, web config); the engine discovers demos at runtime; every query is scoped to one `demo_id` + visibility set. → shows architecture/extensibility thinking.
5. **"How do you know it's good?"** Two-layer eval: a substring section oracle for data integrity + golden datasets with an assertion DSL and an LLM judge for recall@k, faithfulness, citation precision, and refusal accuracy. → shows eval-driven development (rare and valued).
6. **"What's next?"** Contextual embeddings (Anthropic-style situating context + contextual BM25) and structure-aware/parent-document chunking — *gated on the eval harness*. → shows you read the literature and ship measured improvements. (See the companion docs.)
7. **"Why a Raspberry Pi?"** Forced real cost/latency discipline: models via API (no GPU), DB in Docker, app bare-metal (Pi OOMs on torch+Next builds), public via Cloudflare Tunnel. → shows you can ship under constraints.

---

## 5. Social media

### 5a. LinkedIn (narrative + CTA)

> Most "AI chatbot" demos will happily make up an answer. I wanted the opposite: an assistant that answers **only** from a trusted source — and **cites every claim** — or politely refuses.
>
> So I built a multi-domain **Retrieval-Augmented Generation** platform. One engine, six grounded assistants: Indian law (the new 2023 BNS/BNSS/BSA codes), health (WHO fact sheets), insurance (IRDAI policies), NCERT study help, customer support, and French.
>
> Under the hood:
> → **Hybrid retrieval** — dense embeddings (bge-m3 + pgvector/HNSW) *and* keyword BM25, fused with Reciprocal Rank Fusion, then a cross-encoder reranker.
> → **Grounding & guardrails** — cites only retrieved provisions, refuses when context is thin, and flags *repealed* laws (e.g. old IPC → new BNS).
> → **Access control** — document-level public/internal/confidential.
> → **Evaluation built in** — golden datasets + an LLM judge measuring retrieval recall, faithfulness, and refusal accuracy.
> → **Runs on a Raspberry Pi** — no GPU, all models via API.
>
> Adding a whole new domain takes zero engine code — just a config folder. The most fun part was making it *honest*: I wrote tests that fail the build if it answers a question it shouldn't.
>
> Repo + write-ups on chunking strategy, contextual embeddings, and evaluation 👇 [link]
>
> \#RAG #LLM #AIEngineering #MachineLearning #Python #VectorSearch

### 5b. X/Twitter thread

1/ I built a RAG platform that *won't* hallucinate. It answers only from a trusted corpus, cites every claim, and refuses when it can't. Six domains, one engine. 🧵
2/ Flagship: **Vidhi** — Q&A on India's brand-new 2023 criminal codes (BNS/BNSS/BSA) + Constitution + civil statutes. Ask about murder under BNS → it cites **s.103**. Ask something out-of-corpus → it refuses instead of guessing.
3/ Retrieval is **hybrid**: dense (bge-m3 + pgvector/HNSW) ⊕ BM25, fused with Reciprocal Rank Fusion, then a cross-encoder reranker. Dense finds meaning; BM25 finds exact section numbers. You need both.
4/ One nice trick: it runs on **ParadeDB** — pgvector *and* BM25 inside a single Postgres. No separate vector DB + search cluster to sync.
5/ Safety isn't a vibe, it's tested: golden datasets + an assertion DSL + an LLM judge measure recall@k, faithfulness, citation precision, and **refusal accuracy**. Answering an out-of-corpus question fails the build.
6/ It's multi-tenant by **config** — a new domain (health, insurance, French…) is a folder: corpus + section grammar + prompts. Zero engine changes.
7/ And it all runs on a **Raspberry Pi** via Cloudflare Tunnel — models over API, no GPU at query time.
8/ Write-ups on chunking strategy, contextual embeddings, and the eval harness in the repo 👇 [link]

### 5c. One-shot post (X / Threads)
> Built a RAG system that refuses to hallucinate: hybrid retrieval (dense + BM25 + RRF) → reranker → Claude, with citation grounding, refusal guardrails, and a golden-dataset eval that fails CI if it answers out-of-corpus. 6 domains, 1 config-driven engine, running on a Raspberry Pi. [link]

### 5d. Show HN / r/MachineLearning
> **Show HN: A multi-domain RAG engine with built-in evaluation and guardrails (runs on a Pi)**
> I got tired of RAG demos that hallucinate, so I built one that cites every claim and refuses when context is insufficient. Hybrid retrieval (pgvector HNSW + ParadeDB BM25 → RRF → cross-encoder rerank), config-driven multi-tenancy (6 domains incl. Indian law on the 2023 codes), document-level access control, and a golden-dataset eval harness (recall@k / faithfulness / refusal accuracy). Deployed on a Raspberry Pi via Cloudflare Tunnel. Write-ups on chunking + contextual embeddings + evals included. Feedback welcome.

### 5e. GitHub repo metadata
- **Description:** "Production-grade, multi-domain RAG: hybrid retrieval (pgvector+BM25+RRF), reranking, citation grounding, refusal guardrails, and golden-dataset evals. Runs on a Raspberry Pi."
- **Topics:** `rag` `retrieval-augmented-generation` `llm` `vector-search` `pgvector` `bm25` `hybrid-search` `reranking` `fastapi` `nextjs` `paradedb` `embeddings` `llm-evaluation` `ai-safety` `claude`

---

## 6. What to show (portfolio presentation)

Credibility comes from *seeing it work honestly*:
- **A live link** (your Cloudflare Tunnel) — let people try it. Seed the empty state with suggested questions (already in `web_config.ts`).
- **The refusal in action.** Record a GIF: a grounded, cited answer, then an out-of-corpus question getting refused, then a repealed-law query getting flagged. The *refusal* is the differentiator — lead with it.
- **The retrieved-chunks panel.** Showing scores/citations proves it's really retrieving, not winging it.
- **An eval screenshot/table.** The ablation matrix from [evals-strategy.md](evals-strategy.md) (hybrid vs vanilla vs +rerank) is the most senior-looking artifact you can show.
- **README badges + architecture diagram** (already in the README).

---

## 7. Differentiators cheat-sheet (vs a typical RAG demo)

| Typical demo | This project |
|--------------|--------------|
| Embed PDFs, call an LLM | Hybrid retrieval + RRF + cross-encoder rerank |
| Answers everything (hallucinates) | Cites every claim; refuses when unsure; flags repealed law |
| One dataset | Six domains from one config-driven engine |
| No access control | Document-level public/internal/confidential |
| "Looks good to me" | Golden-dataset eval: recall@k, faithfulness, refusal accuracy, CI gates |
| Runs on a beefy cloud box | Runs on a Raspberry Pi, models via API, no GPU |

---

## 8. Cautions

- **Don't invent metrics.** Run `scripts/eval.py`, then quote the real recall@k / refusal accuracy. Round honestly.
- **Keep the disclaimers.** The legal and health demos are information tools, not professional advice — say so (the app already does). It reads as *responsible*, not weak.
- **Credit the corpus sources** (Indian government statutes, WHO fact sheets, IRDAI wordings, NCERT) — using public, citable sources is part of the "grounded and honest" story.
- **Lead with the problem, not the stack.** "It won't hallucinate" hooks people; the tech stack is the proof, not the pitch.
