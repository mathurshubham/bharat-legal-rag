"""
Embedding via OpenRouter API (default, Pi-compatible) or local qwen3 fallback.

OPENROUTER_API_KEY set → OpenRouter embeddings API, zero model loading.
Unset                  → local qwen3-embedding-0.6b (requires 1.2GB RAM, Mac/GPU).

Production model: baai/bge-m3 (1024 dim, multilingual, stable on OpenRouter)

IMPORTANT — asymmetry mechanism:
  OpenRouter silently ignores the input_type parameter for bge-m3 (verified:
  same string with input_type=passage vs query returns cosine=1.000).
  Asymmetry is achieved via a manual query prefix prepended in embed_query().
  input_type is kept in the request body as forward-compat only — do NOT
  remove the prefix on the assumption that input_type carries the signal.
"""
from .config import settings

_OR_KEY = settings.openrouter_api_key
_OR_URL = "https://openrouter.ai/api/v1/embeddings"
_OR_MODEL = settings.embed_model

_LOCAL_MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
# Dev-only fallback prefix — domain-neutral
_LOCAL_QUERY_PREFIX = "Instruct: Retrieve relevant passages for a retrieval query\nQuery: "
_LOCAL_DOC_PREFIX = ""

# bge-m3 instruction prefix for query-side asymmetry (the real mechanism — see module docstring)
_BGE_QUERY_PREFIX = "Represent this query for retrieving relevant passages: "

EMBED_DIM = 1024
_BATCH_SIZE = settings.embed_batch_size

import httpx

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
    import time
    results: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        for attempt in range(3):
            resp = httpx.post(
                _OR_URL,
                headers={
                    "Authorization": f"Bearer {_OR_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://rag-demos",
                    "X-Title": "RAG Demos",
                },
                json={
                    "model": _OR_MODEL,
                    "input": batch,
                    "input_type": input_type,   # inert for bge-m3 on OpenRouter; kept for forward-compat
                    "dimensions": EMBED_DIM,
                },
                timeout=120.0,
            )
            if resp.status_code == 429 or resp.status_code >= 500:
                wait = 2 ** attempt * 5
                print(f"  [embed] HTTP {resp.status_code}, retry in {wait}s (attempt {attempt+1}/3)")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            payload = resp.json()
            if "data" not in payload:
                raise RuntimeError(f"Unexpected embed response (no 'data'): {payload}")
            data = sorted(payload["data"], key=lambda x: x["index"])
            results.extend([float(v) for v in item["embedding"]] for item in data)
            break
        else:
            raise RuntimeError(f"Embedding failed after 3 retries for batch starting at {i}")
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
        batch_size=8,
        show_progress_bar=True,
    )
    return vecs.tolist()


def embed_query(texts: list[str]) -> list[list[float]]:
    if _OR_KEY:
        # Prepend instruction prefix — this is the ONLY mechanism producing query/passage
        # asymmetry for bge-m3 on OpenRouter. Removing the prefix collapses to symmetric
        # encoding. See module docstring.
        prefixed = [_BGE_QUERY_PREFIX + t for t in texts]
        return _or_embed(prefixed, "query")
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
