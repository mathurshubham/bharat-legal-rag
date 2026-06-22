"""
Embedding via OpenRouter API (default, Pi-compatible) or local qwen3 fallback.

OPENROUTER_API_KEY set → OpenRouter embeddings API, zero model loading.
Unset                  → local qwen3-embedding-0.6b (requires 1.2GB RAM, Mac/GPU).

Free model: nvidia/llama-nemotron-embed-vl-1b-v2:free (2048 dims, Matryoshka)
            requested at 1024 dims to match DB schema.
"""
import os

import httpx

_OR_KEY = os.getenv("OPENROUTER_API_KEY", "")
_OR_URL = "https://openrouter.ai/api/v1/embeddings"
_OR_MODEL = os.getenv("EMBED_MODEL", "nvidia/llama-nemotron-embed-vl-1b-v2:free")

_LOCAL_MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
_LOCAL_QUERY_PREFIX = "Instruct: Retrieve relevant passages for a legal query\nQuery: "
_LOCAL_DOC_PREFIX = ""

EMBED_DIM = 1024
_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "64"))  # larger batches fine for API

# ── Local model (lazy, only loaded when OPENROUTER_API_KEY not set) ───────────
_embedder = None


def _best_device() -> str:
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def get_embedder():
    global _embedder
    if _embedder is None:
        import torch
        from sentence_transformers import SentenceTransformer
        device = _best_device()
        dtype = torch.float16 if device in ("mps", "cuda") else torch.float32
        _embedder = SentenceTransformer(
            _LOCAL_MODEL_ID,
            trust_remote_code=True,
            device=device,
            model_kwargs={"torch_dtype": dtype},
        )
        _embedder.max_seq_length = 512
    return _embedder


# ── OpenRouter embeddings API ─────────────────────────────────────────────────

def _or_embed(texts: list[str], input_type: str) -> list[list[float]]:
    """Batch texts through OpenRouter embeddings endpoint."""
    results: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        resp = httpx.post(
            _OR_URL,
            headers={
                "Authorization": f"Bearer {_OR_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://legal-rag-demo",
                "X-Title": "Legal RAG Demo",
            },
            json={
                "model": _OR_MODEL,
                "input": batch,
                "input_type": input_type,
                "dimensions": EMBED_DIM,
            },
            timeout=60.0,
        )
        resp.raise_for_status()
        data = sorted(resp.json()["data"], key=lambda x: x["index"])
        results.extend([float(v) for v in item["embedding"]] for item in data)
    return results


# ── Public API ────────────────────────────────────────────────────────────────

def embed_doc(texts: list[str]) -> list[list[float]]:
    if _OR_KEY:
        return _or_embed(texts, "passage")
    model = get_embedder()
    vecs = model.encode(
        texts,
        prompt=_LOCAL_DOC_PREFIX,
        normalize_embeddings=True,
        batch_size=int(os.getenv("EMBED_BATCH_SIZE", "8")),
        show_progress_bar=True,
    )
    return vecs.tolist()


def embed_query(texts: list[str]) -> list[list[float]]:
    if _OR_KEY:
        return _or_embed(texts, "query")
    model = get_embedder()
    vecs = model.encode(
        texts,
        prompt=_LOCAL_QUERY_PREFIX,
        normalize_embeddings=True,
        batch_size=8,
        show_progress_bar=False,
    )
    return vecs.tolist()


def get_manifest() -> dict:
    if _OR_KEY:
        return {"model": _OR_MODEL, "dim": EMBED_DIM, "normalize": True, "backend": "openrouter"}
    return {"model": _LOCAL_MODEL_ID, "dim": EMBED_DIM, "normalize": True, "backend": "local"}
