#!/usr/bin/env python3
"""
Ingest pipeline: load→segment→sub-chunk→embed→store.
Run: uv run python -m scripts.ingest --demo law
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Callable

import psycopg
import tiktoken
import yaml
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.embed import embed_doc, get_manifest

DB_URL = os.environ["DATABASE_URL"]
CHUNK_TOKENS = 512
OVERLAP_TOKENS = 64
_enc = tiktoken.get_encoding("cl100k_base")

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def tokenize(text: str) -> list[int]:
    return _enc.encode(text)


def decode_tokens(tokens: list[int]) -> str:
    return _enc.decode(tokens)


# ── Manifest loading ──────────────────────────────────────────────────────────

def load_manifest(demo_id: str) -> dict:
    path = REPO_ROOT / "demos" / demo_id / "manifest.yaml"
    if not path.exists():
        print(f"Manifest not found: {path}")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def load_hooks(demo_id: str) -> dict[str, Callable]:
    """Load per-demo normalizer functions from ingest_hooks.py if present."""
    hooks_path = REPO_ROOT / "demos" / demo_id / "ingest_hooks.py"
    if not hooks_path.exists():
        return {}
    spec = importlib.util.spec_from_file_location("ingest_hooks", hooks_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {name: fn for name, fn in vars(module).items() if callable(fn) and not name.startswith("_")}


# ── Section segmentation ──────────────────────────────────────────────────────

def _compile_patterns(raw: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.MULTILINE) for p in raw]


def segment_text(text: str, doc_id: str, manifest: dict, hooks: dict) -> list[dict]:
    """Split text into sections using manifest-driven patterns."""
    section_cfg = manifest["section"]
    patterns = _compile_patterns(section_cfg["patterns"])
    normalizer_overrides = section_cfg.get("normalizer_overrides", {})
    format_overrides = section_cfg.get("format_overrides", {})
    format_default = section_cfg.get("format_default", "{short} s.{n}")
    doc_shorts = manifest.get("doc_shorts", {})

    # Apply normalizer if specified for this doc
    normalizer_name = normalizer_overrides.get(doc_id)
    if normalizer_name and normalizer_name in hooks:
        text = hooks[normalizer_name](text)

    # For docs with a format override, always use the matching pattern
    if doc_id in format_overrides:
        # Find the first pattern that produces matches for this doc_id's override
        # (e.g. CONSTITUTION always uses the Article pattern)
        best_pat = max(patterns, key=lambda p: len(p.findall(text)))
    else:
        best_pat = max(patterns, key=lambda p: len(p.findall(text)))

    matches = list(best_pat.finditer(text))

    if not matches:
        return [{"section_ref": f"{doc_id}:full", "text": text}]

    short = doc_shorts.get(doc_id, doc_id)
    fmt = format_overrides.get(doc_id, format_default)

    segments = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        ref_label = m.group(1) if m.lastindex else m.group(0).strip()
        section_ref = fmt.format(short=short, n=ref_label)
        segments.append({"section_ref": section_ref, "text": text[start:end].strip()})
    return segments


# ── Sub-chunking ──────────────────────────────────────────────────────────────

def sub_chunk(section: dict) -> list[dict]:
    """Sub-chunk a section into ~CHUNK_TOKENS pieces with OVERLAP_TOKENS overlap."""
    tokens = tokenize(section["text"])
    if len(tokens) <= CHUNK_TOKENS:
        return [{"section_ref": section["section_ref"], "text": section["text"], "chunk_index": 0}]

    chunks = []
    start = 0
    idx = 0
    while start < len(tokens):
        end = min(start + CHUNK_TOKENS, len(tokens))
        chunk_text = decode_tokens(tokens[start:end])
        chunks.append({
            "section_ref": section["section_ref"],
            "text": chunk_text,
            "chunk_index": idx,
        })
        if end == len(tokens):
            break
        start += CHUNK_TOKENS - OVERLAP_TOKENS
        idx += 1
    return chunks


# ── Document loading ──────────────────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Empty dict if no frontmatter."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    if not isinstance(fm, dict):
        return {}, text
    return fm, text[m.end():]


def load_doc(path: Path) -> tuple[str, dict]:
    """Return (body_text, frontmatter_dict). Frontmatter only parsed for .md files."""
    if path.suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages), {}
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        fm, body = _split_frontmatter(raw)
        return body, fm
    return raw, {}


_VALID_VISIBILITY = ("public", "internal", "confidential")


def _resolve_visibility(doc_id: str, frontmatter: dict, manifest: dict) -> str:
    """Per-doc visibility: frontmatter > manifest.doc_visibility > 'public'."""
    v = frontmatter.get("visibility")
    if v is None:
        v = manifest.get("doc_visibility", {}).get(doc_id)
    if v is None:
        return "public"
    if v not in _VALID_VISIBILITY:
        raise ValueError(f"Invalid visibility {v!r} for doc {doc_id}; expected one of {_VALID_VISIBILITY}")
    return v


# ── Per-document ingest ───────────────────────────────────────────────────────

_METADATA_PASSTHROUGH = ("effective_date", "superseded_by", "audience", "version")


def _stringify(v):
    import datetime
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v


def _build_metadata(frontmatter: dict) -> dict:
    """Pluck whitelisted frontmatter keys into per-chunk metadata. Dates → ISO strings."""
    md = {}
    for k in _METADATA_PASSTHROUGH:
        if k in frontmatter:
            md[k] = _stringify(frontmatter[k])
    return md


def ingest_doc(conn: psycopg.Connection, demo_id: str, doc_id: str, path: Path,
               manifest: dict, hooks: dict) -> int:
    print(f"  Loading {path.name}...")
    raw, frontmatter = load_doc(path)
    visibility = _resolve_visibility(doc_id, frontmatter, manifest)
    metadata = _build_metadata(frontmatter)
    print(f"  visibility={visibility}" + (f"  metadata={list(metadata)}" if metadata else ""))

    segments = segment_text(raw, doc_id, manifest, hooks)
    print(f"  {len(segments)} sections")

    all_chunks = []
    for seg in segments:
        all_chunks.extend(sub_chunk(seg))
    print(f"  {len(all_chunks)} sub-chunks")

    embed_manifest = get_manifest()
    texts = [c["text"] for c in all_chunks]
    vecs = embed_doc(texts)

    doc_title = manifest["doc_titles"].get(doc_id, doc_id)
    metadata_json = json.dumps(metadata)
    rows = []
    for chunk, vec in zip(all_chunks, vecs):
        rows.append((
            demo_id, doc_id, doc_title,
            chunk["section_ref"], chunk["chunk_index"],
            chunk["text"], len(tokenize(chunk["text"])),
            visibility, metadata_json,
            vec, json.dumps(embed_manifest),
            embed_manifest["model"],
        ))

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO chunks
              (demo_id, doc_id, doc_title, section_ref, chunk_index, content, tokens,
               visibility, metadata,
               embedding, embed_manifest, embed_model)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::vector, %s::jsonb, %s)
            """,
            rows,
        )
    conn.commit()
    print(f"  inserted {len(rows)} rows")
    return len(rows)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", required=True, help="Demo id (e.g. law)")
    parser.add_argument("--doc", help="Ingest single doc by stem (e.g. CONSTITUTION)")
    args = parser.parse_args()

    demo_id = args.demo.lower()
    manifest = load_manifest(demo_id)
    hooks = load_hooks(demo_id)
    corpus_dir = REPO_ROOT / "demos" / demo_id / "corpus" / "clean"

    if not corpus_dir.exists():
        print(f"Corpus dir not found: {corpus_dir}")
        sys.exit(1)

    SUPPORTED_EXTS = {".pdf", ".txt", ".md"}
    all_docs = sorted(
        p for p in corpus_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    )

    if args.doc:
        stem = args.doc.upper()
        docs = [p for p in all_docs if p.stem.upper() == stem or p.stem.upper().startswith(stem)]
        if not docs:
            print(f"No file matching {stem} under {corpus_dir}")
            sys.exit(1)
        docs = docs[:1]
    else:
        docs = all_docs
        if not docs:
            print(f"No supported files ({sorted(SUPPORTED_EXTS)}) under {corpus_dir}")
            sys.exit(1)

    conn = psycopg.connect(DB_URL)
    total = 0
    for path in sorted(docs):
        doc_id = path.stem.upper().replace("-", "_").replace(" ", "_")
        print(f"\n[{doc_id}]")
        total += ingest_doc(conn, demo_id, doc_id, path, manifest, hooks)
    conn.close()
    print(f"\nDone. {total} total chunks inserted.")


if __name__ == "__main__":
    main()
