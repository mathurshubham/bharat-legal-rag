import os
from functools import lru_cache

import torch
from sentence_transformers import SentenceTransformer

_MODEL_ID = os.getenv("EMBED_MODEL", "Qwen/Qwen3-Embedding-0.6B")

# Instruction prefixes per qwen3 docs
_QUERY_PREFIX = "Instruct: Retrieve relevant passages for a legal query\nQuery: "
_DOC_PREFIX = ""

_embedder: SentenceTransformer | None = None

EMBED_DIM = 1024


def _best_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _model_dtype(device: str) -> torch.dtype:
    # float16 on MPS halves model memory (~1.2 GB vs ~2.4 GB for qwen3-0.6b)
    if device in ("mps", "cuda"):
        return torch.float16
    return torch.float32


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        device = _best_device()
        _embedder = SentenceTransformer(
            _MODEL_ID,
            trust_remote_code=True,
            device=device,
            model_kwargs={"torch_dtype": _model_dtype(device)},
        )
        _embedder.max_seq_length = 512
    return _embedder


# Smaller batch on MPS to keep peak activation memory under 20 GB
_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "8"))


def _embed(texts: list[str], prompt_prefix: str) -> list[list[float]]:
    model = get_embedder()
    vecs = model.encode(
        texts,
        prompt=prompt_prefix,
        normalize_embeddings=True,
        batch_size=_BATCH_SIZE,
        show_progress_bar=True,
    )
    return vecs.tolist()


def embed_doc(texts: list[str]) -> list[list[float]]:
    return _embed(texts, _DOC_PREFIX)


def embed_query(texts: list[str]) -> list[list[float]]:
    return _embed(texts, _QUERY_PREFIX)


def get_manifest() -> dict:
    return {"model": _MODEL_ID, "dim": EMBED_DIM, "normalize": True}
