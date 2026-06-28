from contextlib import asynccontextmanager

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import REPO_ROOT, settings
from .db import close_pool, get_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    # Warm local embedder only when OpenRouter API key not set
    if not settings.openrouter_api_key:
        from .embed import get_embedder
        get_embedder()
    yield
    await close_pool()


app = FastAPI(title="RAG Demos API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/api/demos")
async def list_demos():
    """Return all registered demos from the demos/ directory."""
    demos_root = REPO_ROOT / "demos"
    demos = []
    if demos_root.exists():
        for d in sorted(demos_root.iterdir()):
            manifest_path = d / "manifest.yaml"
            if d.is_dir() and manifest_path.exists():
                with open(manifest_path) as f:
                    m = yaml.safe_load(f)
                demos.append({
                    "id": m.get("demo_id", d.name),
                    "title": m.get("title", d.name),
                    "description": m.get("description", ""),
                })
    return {"demos": demos}


@app.get("/api/{demo}/corpus")
async def corpus_info(demo: str):
    """Return all ingested documents for a demo with chunk counts — live from DB."""
    from psycopg.rows import dict_row
    pool = await get_pool()
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        rows = await (await conn.execute(
            """
            SELECT doc_id, doc_title,
                   count(*) AS chunk_count,
                   count(DISTINCT section_ref) AS section_count
            FROM chunks
            WHERE demo_id = %s
            GROUP BY doc_id, doc_title
            ORDER BY doc_title
            """,
            (demo.lower(),),
        )).fetchall()
        total = await (await conn.execute(
            "SELECT count(*) AS n FROM chunks WHERE demo_id = %s",
            (demo.lower(),),
        )).fetchone()

    return {
        "demo_id": demo.lower(),
        "documents": [dict(r) for r in rows],
        "total_chunks": total["n"] if total else 0,
    }


from .dataset import dataset_info             # noqa: E402
from .query import router as query_router     # noqa: E402
app.add_api_route("/api/{demo}/dataset", dataset_info, methods=["GET"])
app.include_router(query_router)


# ── Teacher dashboard — chapter outline grouped by Leçon + chunk type ─────────
@app.get("/api/{demo}/chapters")
async def chapter_outline(demo: str, board: str | None = None):
    """Return chapter outline for browsing — used by teacher dashboard.

    Output:
      { "chapters": [
          { "id": "Leçon 6", "doc_id": "CBSE_10_ENTREJEUNES", "doc_title": "...",
            "board": "cbse", "level": "A2",
            "sections": [
              { "section_ref": "...", "type": "exercise", "skill": "mixed",
                "preview": "..."} ]
          },
          ... ]
      }
    """
    from psycopg.rows import dict_row
    pool = await get_pool()
    where = ["demo_id = %s"]
    params: list = [demo.lower()]
    if board and board not in ("all", ""):
        where.append("metadata->>'board' = %s")
        params.append(board)
    sql = f"""
        SELECT doc_id, doc_title,
               COALESCE(NULLIF(regexp_replace(section_ref, '.*§(Leçon \\d+).*', '\\1'), section_ref), 'Other') AS chapter,
               metadata->>'board'  AS board,
               metadata->>'level'  AS level,
               metadata->>'type'   AS type,
               metadata->>'skill'  AS skill,
               section_ref,
               LEFT(content, 120) AS preview
        FROM chunks
        WHERE {' AND '.join(where)}
        ORDER BY doc_id, chapter, section_ref
    """
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        rows = await (await conn.execute(sql, params)).fetchall()

    # Group by (doc_id, chapter)
    grouped: dict[tuple, dict] = {}
    for r in rows:
        key = (r["doc_id"], r["chapter"])
        if key not in grouped:
            grouped[key] = {
                "id": r["chapter"],
                "doc_id": r["doc_id"],
                "doc_title": r["doc_title"],
                "board": r["board"],
                "level": r["level"],
                "sections": [],
            }
        grouped[key]["sections"].append({
            "section_ref": r["section_ref"],
            "type": r["type"],
            "skill": r["skill"],
            "preview": r["preview"],
        })
    return {"demo_id": demo.lower(), "chapters": list(grouped.values())}


# ── Question generator (iter 8) ─────────────────────────────────────────────
from pydantic import BaseModel as _BM   # noqa: E402


class GenQuestionsReq(_BM):
    chapter: str | None = None       # e.g. "Leçon 6" or null = use entire corpus
    board: str | None = None         # cbse | ib | None=all
    count: int = 10
    difficulty: str | None = None    # A1 | A2 | B1 | B2 | null
    question_types: list[str] | None = None   # ["mcq","fill_in","short","essay"]
    language_mode: str = "bilingual"


@app.post("/api/{demo}/generate-questions")
async def generate_questions(
    demo: str,
    req: GenQuestionsReq,
    cf_account_id: str | None = None,
    cf_gateway_id: str | None = None,
    x_openrouter_key: str | None = None,
):
    """Build a question bank from indexed chunks. Powers teacher question-gen UI."""
    from fastapi import Header  # type: ignore
    from .retrieval import retrieve as _retrieve
    from .gateway import chat_completion
    from .config import settings as _settings
    import os

    key = x_openrouter_key or _settings.openrouter_api_key
    if not key:
        return {"error": "OpenRouter key required"}

    seed_query = req.chapter or "chapter overview"
    chunks = await _retrieve(
        seed_query, demo_id=demo.lower(),
        mode="hybrid", top_k=40,
        visibility=["public"],
        openrouter_key=key,
        cf_account_id=cf_account_id,
        cf_gateway_id=cf_gateway_id,
        board=req.board,
        section_filter=req.chapter,
    )
    context = "\n\n---\n\n".join(
        f"[{c['section_ref']}]\n{c['content']}" for c in chunks[:15]
    )

    qtypes = ", ".join(req.question_types or ["mcq", "fill_in", "short"])
    sys_prompt = f"""You are an exam-question writer for French language teachers.
From the indexed textbook chunks below, generate {req.count} questions.

Constraints:
- Question types: {qtypes}
- Difficulty: {req.difficulty or 'mixed'}
- Chapter scope: {req.chapter or 'any'}
- Board: {req.board or 'any'}
- Language: {req.language_mode}
- Every question must cite its source section_ref in parentheses.
- After all questions, write an "## Answer key" section with brief, defensible answers.

Format:
1. <question> _(section_ref)_
2. ...
## Answer key
1. <answer>
2. ...

## Source chunks
{context}
"""
    result = await chat_completion(
        messages=[{"role": "user", "content": sys_prompt}],
        model=os.getenv("GEN_MODEL", "deepseek/deepseek-v3.2"),
        openrouter_key=key,
        account_id=cf_account_id,
        gateway_id=cf_gateway_id,
        max_tokens=2500,
        temperature=0.4,
    )
    return {
        "questions_markdown": result["text"],
        "chunks_used": [{"section_ref": c["section_ref"], "doc_title": c["doc_title"]} for c in chunks[:15]],
        "config": {
            "chapter": req.chapter, "board": req.board,
            "count": req.count, "difficulty": req.difficulty,
            "question_types": req.question_types or ["mcq", "fill_in", "short"],
        },
    }
