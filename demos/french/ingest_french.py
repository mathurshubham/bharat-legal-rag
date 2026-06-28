#!/usr/bin/env python3
"""French-specific ingestion: markdown-header-aware + atomic-block + contextual headers.

ISOLATED from core scripts/ingest.py. Self-contained for the french demo only.
No schema changes — uses existing chunks table; board/header path stored in metadata JSONB.

Pipeline:
  load .md → NFC normalize
            → split by markdown heading hierarchy (## / ### / ####)
            → group into sections carrying a header path
            → protect atomic blocks (À TOI / Activity / Questions de compréhension / Test / Objectifs / tables)
            → sentence-aware sub-chunking with 400-token target, 60-token overlap
            → prepend contextual header `[doc_title — header_path]` to text before embedding
            → store original chunk text in `content`; contextual text NOT stored (embedded only)

Run:
  DATABASE_URL=... uv run --project apps/api python demos/french/ingest_french.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import psycopg
import tiktoken
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "apps/api"))
from app.embed import embed_doc, get_manifest  # noqa: E402

DEMO_ID = "french"
CORPUS_CLEAN = REPO_ROOT / "demos" / DEMO_ID / "corpus" / "clean"
MANIFEST_PATH = REPO_ROOT / "demos" / DEMO_ID / "manifest.yaml"

TARGET_TOKENS = 400         # smaller than statute default — textbook units shorter
OVERLAP_TOKENS = 60         # 15% overlap
MAX_TOKENS = 600            # never emit a chunk larger than this
_enc = tiktoken.get_encoding("cl100k_base")


def tok_len(s: str) -> int:
    return len(_enc.encode(s))


# ── Heading parsing ───────────────────────────────────────────────────────────

# Atomic blocks: chunks anchored on these heading texts should NOT be split.
# Whole block stays together (even if > target_tokens).
ATOMIC_HEADING_PATTERNS = [
    re.compile(r"^\s*[#*]*\s*(à\s*toi|atoi)\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*activity\s+\d+", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*activit[eé]s?\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*questions?\s+de\s+compr[eé]hension\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*objectifs?\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*test\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*remue[\s-]m[eé]nages?\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*en\s+plus\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*bilan\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*recherche\b", re.IGNORECASE),
    re.compile(r"^\s*[#*]*\s*[ée]preuve\s+orale\b", re.IGNORECASE),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def is_atomic_heading(text: str) -> bool:
    return any(p.search(text) for p in ATOMIC_HEADING_PATTERNS)


_UNIT_CODE_RE = re.compile(r"(\d+[A-C])\s+([A-ZÉÀÂÊÎÔÛ]+)")


def clean_heading(text: str) -> str:
    """Strip markdown emphasis, leaked image alt-text, and other noise from headings."""
    # Drop markdown images entirely
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\*\*|\*|__|_", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    # If heading contains a unit code (e.g. "5A PARTAGE...") preceded by alt-text noise,
    # take only from the unit code onward
    if len(text) > 60:
        m = _UNIT_CODE_RE.search(text)
        if m and m.start() > 20:
            text = text[m.start():].strip()
    return text


@dataclass
class HeadingNode:
    level: int
    text: str
    body: list[str] = field(default_factory=list)
    children: list["HeadingNode"] = field(default_factory=list)
    parent: "HeadingNode | None" = None
    atomic: bool = False


def parse_markdown(md: str) -> HeadingNode:
    """Build a heading-hierarchy tree from markdown. Root has level 0."""
    root = HeadingNode(level=0, text="(root)")
    stack: list[HeadingNode] = [root]

    for line in md.splitlines():
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            text = clean_heading(m.group(2))
            atomic = is_atomic_heading(text)
            node = HeadingNode(level=level, text=text, atomic=atomic)
            # Pop stack until we find a parent with lower level
            while stack and stack[-1].level >= level:
                stack.pop()
            parent = stack[-1] if stack else root
            node.parent = parent
            parent.children.append(node)
            stack.append(node)
        else:
            stack[-1].body.append(line)
    return root


def header_path(node: HeadingNode) -> str:
    """Build breadcrumb path like 'Unité 1A — Qui suis-je ? > Test > Quel serait ton animal totem'."""
    parts = []
    cur = node
    while cur is not None and cur.level > 0:
        parts.append(cur.text)
        cur = cur.parent
    return " > ".join(reversed(parts))


def is_under_atomic(node: HeadingNode) -> bool:
    """True if any ancestor (or self) is marked atomic."""
    cur = node
    while cur is not None:
        if cur.atomic:
            return True
        cur = cur.parent
    return False


# ── Section extraction ────────────────────────────────────────────────────────

@dataclass
class Section:
    doc_id: str
    header_path: str
    body: str               # raw markdown body (no headings of this section's own)
    atomic: bool
    section_ref: str        # used in citations


def collect_sections(root: HeadingNode, doc_id: str, manifest: dict) -> list[Section]:
    """Walk the tree; emit one Section per leaf-ish node OR per atomic-anchor node.

    Leaf-ish = node whose body is non-empty (it has actual content). We do NOT emit
    sections for purely-structural nodes (`# IB DP French B`). Atomic-anchor nodes
    capture all their nested content too.
    """
    sections: list[Section] = []
    short = manifest.get("doc_shorts", {}).get(doc_id, doc_id)

    def emit(node: HeadingNode, body_text: str, atomic: bool) -> None:
        if not body_text.strip():
            return
        path = header_path(node)
        # section_ref = short § <last 2 heading levels of path>
        last_2 = " / ".join(p for p in path.split(" > ")[-2:]) or path
        ref = f"{short} §{last_2}"
        sections.append(Section(
            doc_id=doc_id,
            header_path=path,
            body=body_text,
            atomic=atomic,
            section_ref=ref,
        ))

    def walk(node: HeadingNode):
        if is_under_atomic(node) and node.parent and node.parent.atomic:
            # Skip — atomic ancestor already collected this content
            return
        if node.atomic:
            # Collect entire subtree as one atomic section
            body = collect_subtree_body(node)
            emit(node, body, atomic=True)
            return
        # Non-atomic: emit own body, then recurse into children
        own_body = "\n".join(node.body).strip()
        if own_body:
            emit(node, own_body, atomic=False)
        for child in node.children:
            walk(child)

    def collect_subtree_body(node: HeadingNode) -> str:
        """Concatenate node's own body + all descendant bodies (with their headings re-rendered)."""
        out: list[str] = []
        if node.body:
            out.append("\n".join(node.body))
        for child in node.children:
            out.append(f"{'#' * child.level} {child.text}")
            out.append(collect_subtree_body(child))
        return "\n".join(b for b in out if b.strip())

    for child in root.children:
        walk(child)
    return sections


# ── Sub-chunking ──────────────────────────────────────────────────────────────

PARA_BREAK_RE = re.compile(r"\n\s*\n")
SENT_BREAK_RE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÉÀÂÊÎÔÛ])")


def split_into_paragraphs(text: str) -> list[str]:
    paras = [p.strip() for p in PARA_BREAK_RE.split(text)]
    return [p for p in paras if p]


def split_into_sentences(text: str) -> list[str]:
    # Don't shred markdown table rows
    sents = SENT_BREAK_RE.split(text)
    return [s.strip() for s in sents if s.strip()]


@dataclass
class Chunk:
    section_ref: str
    header_path: str
    text: str
    chunk_index: int


def sub_chunk(section: Section) -> list[Chunk]:
    """If atomic OR body fits, emit one chunk. Else paragraph-pack with overlap."""
    body = section.body.strip()
    tlen = tok_len(body)

    if section.atomic or tlen <= TARGET_TOKENS:
        # Atomic blocks: keep as-is even if > target (capped at MAX_TOKENS only as a
        # safety valve — if a single atomic block is huge, split at paragraph boundary
        # but DON'T sentence-split — atomic = pedagogical unit).
        if tlen <= MAX_TOKENS:
            return [Chunk(section.section_ref, section.header_path, body, 0)]
        # Atomic but huge: paragraph-pack only
        return _pack_paragraphs(section, [body])

    paragraphs = split_into_paragraphs(body)
    return _pack_paragraphs(section, paragraphs)


def _pack_paragraphs(section: Section, paragraphs: list[str]) -> list[Chunk]:
    """Greedy pack paragraphs into ~TARGET_TOKENS chunks, with paragraph-level overlap."""
    chunks: list[Chunk] = []
    buf: list[str] = []
    buf_tokens = 0

    def flush():
        nonlocal buf, buf_tokens
        if not buf:
            return
        text = "\n\n".join(buf).strip()
        if text:
            chunks.append(Chunk(section.section_ref, section.header_path, text, len(chunks)))
        # Tail overlap: keep trailing paragraphs whose tokens sum to ~OVERLAP_TOKENS
        tail = []
        tail_tokens = 0
        for p in reversed(buf):
            pt = tok_len(p)
            if tail_tokens + pt > OVERLAP_TOKENS and tail:
                break
            tail.insert(0, p)
            tail_tokens += pt
        buf = tail
        buf_tokens = tail_tokens

    for p in paragraphs:
        pt = tok_len(p)
        # If a single paragraph already exceeds MAX_TOKENS, fall back to sentence split
        if pt > MAX_TOKENS:
            # Flush current buf, then sentence-pack this paragraph
            flush()
            sents = split_into_sentences(p)
            for s in sents:
                st = tok_len(s)
                if buf_tokens + st > TARGET_TOKENS and buf:
                    flush()
                buf.append(s)
                buf_tokens += st
            continue
        if buf_tokens + pt > TARGET_TOKENS and buf:
            flush()
        buf.append(p)
        buf_tokens += pt
    if buf:
        text = "\n\n".join(buf).strip()
        if text:
            chunks.append(Chunk(section.section_ref, section.header_path, text, len(chunks)))
    return chunks


# ── Contextual header ─────────────────────────────────────────────────────────

def board_of(doc_id: str) -> str:
    if doc_id.startswith("CBSE_"):
        return "cbse"
    if doc_id.startswith("IB_"):
        return "ib"
    return "other"


def contextualize(doc_title: str, chunk: Chunk, board: str) -> str:
    """Prepend doc_title + header_path before embedding (NOT stored as content)."""
    header = f"[{doc_title} — board:{board} — {chunk.header_path}]"
    return f"{header}\n\n{chunk.text}"


# ── Per-doc ingest ────────────────────────────────────────────────────────────

def normalize_text(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def ingest_doc(conn: psycopg.Connection, doc_id: str, path: Path,
               manifest: dict, embed_manifest: dict) -> int:
    print(f"\n[{doc_id}]  loading {path.name}")
    raw = normalize_text(path.read_text(encoding="utf-8"))
    root = parse_markdown(raw)
    sections = collect_sections(root, doc_id, manifest)
    print(f"  sections: {len(sections)} ({sum(1 for s in sections if s.atomic)} atomic)")

    chunks: list[Chunk] = []
    for sec in sections:
        chunks.extend(sub_chunk(sec))
    print(f"  chunks  : {len(chunks)}  (avg {sum(tok_len(c.text) for c in chunks) // max(1,len(chunks))} tok)")

    doc_title = manifest["doc_titles"].get(doc_id, doc_id)
    board = board_of(doc_id)
    visibility = manifest.get("doc_visibility", {}).get(doc_id, "public")

    # Embed contextualized text
    ctx_texts = [contextualize(doc_title, c, board) for c in chunks]
    print(f"  embedding {len(chunks)} chunks (contextualized)…")
    vecs = embed_doc(ctx_texts)

    rows = []
    for chunk, vec in zip(chunks, vecs):
        metadata = {
            "board": board,
            "header_path": chunk.header_path,
            "demo": DEMO_ID,
        }
        rows.append((
            DEMO_ID, doc_id, doc_title,
            chunk.section_ref, chunk.chunk_index,
            chunk.text, tok_len(chunk.text),
            visibility, json.dumps(metadata),
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
    print(f"  inserted {len(rows)} rows  (board={board})")
    return len(rows)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc", help="Ingest single doc by stem (e.g. CBSE_9_ENTREJEUNES)")
    parser.add_argument("--purge", action="store_true",
                        help="Delete existing french chunks first")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show chunk counts but do not embed/insert")
    args = parser.parse_args()

    if not CORPUS_CLEAN.exists():
        sys.exit(f"corpus/clean not found: {CORPUS_CLEAN}")

    with open(MANIFEST_PATH) as f:
        manifest = yaml.safe_load(f)

    docs = sorted(CORPUS_CLEAN.glob("*.md"))
    if args.doc:
        stem = args.doc.upper()
        docs = [d for d in docs if d.stem.upper() == stem]
        if not docs:
            sys.exit(f"no doc matching {stem}")

    print(f"Found {len(docs)} doc(s) to ingest:")
    for d in docs:
        print(f"  - {d.stem}")

    if args.dry_run:
        # Just parse + chunk-count, no DB
        for path in docs:
            doc_id = path.stem.upper()
            raw = normalize_text(path.read_text(encoding="utf-8"))
            root = parse_markdown(raw)
            sections = collect_sections(root, doc_id, manifest)
            chunks = []
            for sec in sections:
                chunks.extend(sub_chunk(sec))
            print(f"\n[{doc_id}]")
            print(f"  sections: {len(sections)} ({sum(1 for s in sections if s.atomic)} atomic)")
            print(f"  chunks  : {len(chunks)}")
            print(f"  avg tokens: {sum(tok_len(c.text) for c in chunks) // max(1, len(chunks))}")
            print(f"  max tokens: {max((tok_len(c.text) for c in chunks), default=0)}")
            # Show first 3 chunks
            for c in chunks[:3]:
                print(f"    · {c.section_ref}")
                print(f"      [{c.header_path}]")
                print(f"      {c.text[:150]!r}")
        return

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        sys.exit("DATABASE_URL not set")
    conn = psycopg.connect(db_url)
    if args.purge:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chunks WHERE demo_id = %s", (DEMO_ID,))
            n = cur.rowcount
        conn.commit()
        print(f"\nPurged {n} existing french chunks")

    embed_manifest = get_manifest()
    print(f"Embed model: {embed_manifest.get('model')}")

    total = 0
    for path in docs:
        doc_id = path.stem.upper()
        total += ingest_doc(conn, doc_id, path, manifest, embed_manifest)
    conn.close()
    print(f"\nDone. {total} total chunks inserted into chunks table (demo_id={DEMO_ID}).")


if __name__ == "__main__":
    main()
