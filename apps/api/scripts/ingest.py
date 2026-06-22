#!/usr/bin/env python3
"""
Ingest pipeline: load→segment→sub-chunk→embed→store.
Run: uv run python -m scripts.ingest
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import psycopg
import tiktoken
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.embed import embed_doc, get_manifest

DB_URL = os.environ["DATABASE_URL"]
CORPUS_DIR = Path(__file__).parent.parent.parent.parent / "corpus" / "clean"
CHUNK_TOKENS = 512
OVERLAP_TOKENS = 64
_enc = tiktoken.get_encoding("cl100k_base")


def tokenize(text: str) -> list[int]:
    return _enc.encode(text)


def decode_tokens(tokens: list[int]) -> str:
    return _enc.decode(tokens)


# ── section segmentation ────────────────────────────────────────────────────

_SECTION_PATTERNS = [
    # BNS / IPC / BNSS / BSA style: "1.", "103.", "Section 1."
    re.compile(r"^(?:Section\s+)?(\d+[A-Z]?)\.\s", re.MULTILINE),
    # Constitution (after normalisation): "Article 1", "Article 21A"
    re.compile(r"^Article\s+(\d+[A-Z]?)\b", re.MULTILINE),
    # Schedule / Part headers — treated as a single segment
    re.compile(r"^(Schedule\s+[IVXLC]+|PART\s+[IVXLC]+)\b", re.MULTILINE),
]

# Matches article numbers that appear inline in the diglot Constitution PDF
# e.g. "...previous text.12. Right to equality.—" or "TERRITORY1. Name and"
_CONSTITUTION_ARTICLE_INLINE = re.compile(
    r"(?<!\d)(\d{1,3}[A-Z]?)\.\s+(?=[A-Z][a-z]|\[)"
)


def _normalise_constitution(text: str) -> str:
    """
    The diglot Constitution PDF collapses article numbers inline.
    Insert a newline+sentinel before each article number so the standard
    line-anchored pattern can find them.
    """
    # Strip leading page numbers: lines that are just digits
    text = re.sub(r"^\d+\s*\n", "", text, flags=re.MULTILINE)
    # Insert newline before inline article numbers
    text = _CONSTITUTION_ARTICLE_INLINE.sub(r"\nArticle \1. ", text)
    return text


def segment_text(text: str, doc_id: str) -> list[dict]:
    """Split text into sections, returning list of {section_ref, text}."""
    if doc_id == "CONSTITUTION":
        text = _normalise_constitution(text)
        pat = _SECTION_PATTERNS[1]  # Article pattern
    else:
        # pick the pattern that gives the most matches
        pat = max(_SECTION_PATTERNS, key=lambda p: len(p.findall(text)))

    matches = list(pat.finditer(text))

    if not matches:
        return [{"section_ref": f"{doc_id}:full", "text": text}]

    segments = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        ref_label = m.group(1) if m.lastindex else m.group(0).strip()
        if doc_id == "CONSTITUTION":
            section_ref = f"Art. {ref_label}"
        else:
            section_ref = f"{_DOC_SHORT.get(doc_id, doc_id)} s.{ref_label}"
        segments.append({"section_ref": section_ref, "text": text[start:end].strip()})
    return segments


_DOC_SHORT = {
    "BNS_2023": "BNS",
    "BNSS_2023": "BNSS",
    "BSA_2023": "BSA",
    "CONTRACT_ACT_1872": "Contract Act",
    "CONSUMER_PROTECTION_2019": "CP",
    "DPDP_2023": "DPDP",
    "CONSTITUTION": "Constitution",
    "LAW_MAPPINGS": "Mappings",
}


def sub_chunk(section: dict, doc_id: str) -> list[dict]:
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


def load_doc(path: Path) -> str:
    if path.suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


_DOC_TITLES = {
    "BNS_2023": "Bharatiya Nyaya Sanhita 2023",
    "BNSS_2023": "Bharatiya Nagarik Suraksha Sanhita 2023",
    "BSA_2023": "Bharatiya Sakshya Adhiniyam 2023",
    "CONTRACT_ACT_1872": "Indian Contract Act 1872",
    "CONSUMER_PROTECTION_2019": "Consumer Protection Act 2019",
    "DPDP_2023": "Digital Personal Data Protection Act 2023",
    "CONSTITUTION": "Constitution of India",
    "LAW_MAPPINGS": "Law Repeal Mappings Reference",
}


def ingest_doc(conn: psycopg.Connection, doc_id: str, path: Path) -> int:
    print(f"  Loading {path.name}...")
    raw = load_doc(path)
    segments = segment_text(raw, doc_id)
    print(f"  {len(segments)} sections")

    all_chunks = []
    for seg in segments:
        all_chunks.extend(sub_chunk(seg, doc_id))
    print(f"  {len(all_chunks)} sub-chunks")

    # embed in batches
    manifest = get_manifest()
    texts = [c["text"] for c in all_chunks]
    vecs = embed_doc(texts)

    doc_title = _DOC_TITLES.get(doc_id, doc_id)
    rows = []
    for chunk, vec in zip(all_chunks, vecs):
        rows.append((
            doc_id, doc_title, chunk["section_ref"], chunk["chunk_index"],
            chunk["text"], len(tokenize(chunk["text"])),
            vec, json.dumps(manifest),
            manifest["model"],
        ))

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO chunks
              (doc_id, doc_title, section_ref, chunk_index, content, tokens,
               embedding, embed_manifest, embed_model)
            VALUES (%s, %s, %s, %s, %s, %s, %s::vector, %s::jsonb, %s)
            """,
            rows,
        )
    conn.commit()
    print(f"  inserted {len(rows)} rows")
    return len(rows)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", help="Ingest single doc by stem (e.g. CONSTITUTION)")
    args = parser.parse_args()

    if not CORPUS_DIR.exists():
        print(f"Corpus dir not found: {CORPUS_DIR}")
        sys.exit(1)

    if args.doc:
        stem = args.doc.upper()
        matches = list(CORPUS_DIR.glob(f"{stem}*"))
        if not matches:
            print(f"No file matching {stem} in {CORPUS_DIR}")
            sys.exit(1)
        docs = matches[:1]
    else:
        docs = list(CORPUS_DIR.glob("*"))
        if not docs:
            print("No files in corpus/clean/ — add statute files first.")
            sys.exit(1)

    conn = psycopg.connect(DB_URL)
    total = 0
    for path in sorted(docs):
        doc_id = path.stem.upper().replace("-", "_").replace(" ", "_")
        print(f"\n[{doc_id}]")
        total += ingest_doc(conn, doc_id, path)
    conn.close()
    print(f"\nDone. {total} total chunks inserted.")


if __name__ == "__main__":
    main()
