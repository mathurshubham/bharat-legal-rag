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


from .query import router as query_router  # noqa: E402
app.include_router(query_router)
