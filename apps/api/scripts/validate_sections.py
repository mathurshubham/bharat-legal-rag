#!/usr/bin/env python3
"""
Validate that section_refs resolve to correct content.
Asserts on content substrings — not mere ref existence.

Run BEFORE ingest to validate segmented clean text, or AFTER ingest to validate DB.

Usage:
  # validate clean text files (pre-ingest):
  uv run python -m scripts.validate_sections --demo law --source files

  # validate DB (post-ingest):
  uv run python -m scripts.validate_sections --demo law --source db
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def load_checks(demo_id: str) -> list[dict]:
    path = REPO_ROOT / "demos" / demo_id / "validate_checks.yaml"
    if not path.exists():
        print(f"validate_checks.yaml not found: {path}")
        sys.exit(1)
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("checks", [])


def _check_substring(content: str, substring: str) -> bool:
    return substring.lower() in content.lower()


def validate_from_db(demo_id: str, checks: list[dict]) -> list[str]:
    import os
    import psycopg

    db_url = os.environ["DATABASE_URL"]
    conn = psycopg.connect(db_url)
    failures = []

    for check in checks:
        doc_id = check["doc_id"]
        section_ref = check["section_ref"]
        substring = check["substring"]
        desc = check["description"]

        # section_ref="*" = check combined content of all chunks for this doc
        if section_ref == "*":
            rows = conn.execute(
                "SELECT content FROM chunks WHERE demo_id=%s AND doc_id=%s",
                (demo_id, doc_id),
            ).fetchall()
            if not rows:
                failures.append(f"MISSING  {doc_id} (no chunks) — {desc}")
                continue
        else:
            rows = conn.execute(
                "SELECT content FROM chunks WHERE demo_id=%s AND doc_id=%s AND section_ref=%s LIMIT 5",
                (demo_id, doc_id, section_ref),
            ).fetchall()
            if not rows:
                failures.append(f"MISSING  {section_ref} ({doc_id}) — {desc}")
                continue

        combined = " ".join(r[0] for r in rows)
        if not _check_substring(combined, substring):
            failures.append(
                f"BAD_CONTENT  {section_ref} ({doc_id}) — expected '{substring}' — {desc}"
            )

    conn.close()
    return failures


def validate_from_files(demo_id: str, checks: list[dict]) -> list[str]:
    corpus_dir = REPO_ROOT / "demos" / demo_id / "corpus" / "clean"
    if not corpus_dir.exists():
        return [f"corpus/clean/ not found at {corpus_dir}"]

    SUPPORTED_EXTS = {".txt", ".md"}  # validate_from_files reads as text — skip PDFs
    texts: dict[str, str] = {}
    for path in corpus_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTS:
            continue
        doc_id = path.stem.upper().replace("-", "_").replace(" ", "_")
        texts[doc_id] = path.read_text(encoding="utf-8", errors="replace")

    failures = []
    for check in checks:
        doc_id = check["doc_id"]
        section_ref = check["section_ref"]
        substring = check["substring"]
        desc = check["description"]

        if doc_id not in texts:
            failures.append(f"MISSING_FILE  {doc_id} — needed for {section_ref}")
            continue
        if not _check_substring(texts[doc_id], substring):
            failures.append(
                f"BAD_CONTENT  {section_ref} ({doc_id}) — expected '{substring}' — {desc}"
            )
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", required=True, help="Demo id (e.g. law)")
    parser.add_argument("--source", choices=["files", "db"], default="db")
    args = parser.parse_args()

    demo_id = args.demo.lower()
    checks = load_checks(demo_id)

    print(f"Validating {len(checks)} section checks for demo={demo_id!r} from {args.source}...")
    failures = (
        validate_from_db(demo_id, checks)
        if args.source == "db"
        else validate_from_files(demo_id, checks)
    )

    if failures:
        print(f"\nFAILED ({len(failures)}/{len(checks)}):")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    else:
        print(f"\nPASSED — all {len(checks)} checks green. Safe to proceed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
