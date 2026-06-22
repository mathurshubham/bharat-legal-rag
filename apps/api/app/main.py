from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import close_pool, get_pool
from .embed import get_embedder


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    get_embedder()
    yield
    await close_pool()


app = FastAPI(title="Legal RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
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


from .query import router as query_router  # noqa: E402
app.include_router(query_router)
