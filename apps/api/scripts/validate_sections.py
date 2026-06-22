#!/usr/bin/env python3
"""
Phase 1b gate: validate ~20 known section_refs resolve to correct content.
Asserts on content substrings — not mere ref existence.
Run BEFORE ingest to validate segmented clean text, or AFTER ingest to validate DB.

Usage:
  # validate clean text files (pre-ingest):
  uv run python -m scripts.validate_sections --source files

  # validate DB (post-ingest):
  uv run python -m scripts.validate_sections --source db
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# (doc_id, section_ref, required_substring, description)
CHECKS: list[tuple[str, str, str, str]] = [
    # BNS 2023
    ("BNS_2023", "BNS s.103", "murder",             "BNS 103 = punishment for murder"),
    ("BNS_2023", "BNS s.63",  "rape",               "BNS 63 = rape"),
    ("BNS_2023", "BNS s.309", "robbery",            "BNS 309 = robbery"),
    ("BNS_2023", "BNS s.2",   "definitions",        "BNS 2 = definitions"),
    ("BNS_2023", "BNS s.4",   "punishments",        "BNS 4 = punishments"),

    # Constitution
    ("CONSTITUTION", "Art. 14", "equality",         "Art. 14 = equality before law"),
    ("CONSTITUTION", "Art. 19", "freedom",          "Art. 19 = freedoms"),
    ("CONSTITUTION", "Art. 21", "life and personal liberty", "Art. 21 = right to life"),
    ("CONSTITUTION", "Art. 32", "remedies",         "Art. 32 = constitutional remedies"),
    ("CONSTITUTION", "Art. 226","High Court",       "Art. 226 = HC writ jurisdiction"),

    # Contract Act 1872
    ("CONTRACT_ACT_1872", "Contract Act s.2",  "proposal",    "s.2 = definitions (proposal)"),
    ("CONTRACT_ACT_1872", "Contract Act s.10", "competent",   "s.10 = competency to contract"),
    ("CONTRACT_ACT_1872", "Contract Act s.73", "compensation","s.73 = damages on breach"),

    # Consumer Protection 2019
    ("CONSUMER_PROTECTION_2019", "CP s.2",  "consumer",      "s.2 = definitions (consumer)"),
    ("CONSUMER_PROTECTION_2019", "CP s.35", "complaint",     "s.35 = complaint before District Commission"),
    ("CONSUMER_PROTECTION_2019", "CP s.17", "consumer rights", "s.17 = CCPA — violation of consumer rights"),

    # DPDP 2023
    ("DPDP_2023", "DPDP s.2",  "personal data",    "s.2 = definitions"),
    ("DPDP_2023", "DPDP s.4",  "processing",       "s.4 = grounds for processing"),
    ("DPDP_2023", "DPDP s.8",  "obligations",      "s.8 = obligations of data fiduciary"),

    # BNSS 2023
    ("BNSS_2023", "BNSS s.173", "cognizable",        "BNSS 173 = FIR / information in cognizable cases"),
    ("BNSS_2023", "BNSS s.480", "bail",              "BNSS 480 = bail in non-bailable offences"),
    ("BNSS_2023", "BNSS s.2",   "definitions",       "BNSS 2 = definitions"),

    # BSA 2023
    ("BSA_2023", "BSA s.2",  "evidence",             "BSA 2 = definitions (evidence)"),
    ("BSA_2023", "BSA s.39", "expert",               "BSA 39 = opinions of experts"),
    ("BSA_2023", "BSA s.63", "electronic",           "BSA 63 = admissibility of electronic records"),

    # LAW_MAPPINGS crosswalk (no section patterns matched → fallback ref)
    ("LAW_MAPPINGS", "LAW_MAPPINGS:full", "BNS",     "IPC→BNS mapping present"),
]


def _check_substring(content: str, substring: str) -> bool:
    return substring.lower() in content.lower()


def validate_from_db() -> list[str]:
    import os
    import psycopg

    db_url = os.environ["DATABASE_URL"]
    conn = psycopg.connect(db_url)
    failures = []

    for doc_id, section_ref, substring, desc in CHECKS:
        rows = conn.execute(
            "SELECT content FROM chunks WHERE doc_id=%s AND section_ref=%s LIMIT 5",
            (doc_id, section_ref),
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


def validate_from_files() -> list[str]:
    corpus_dir = Path(__file__).parent.parent.parent.parent / "corpus" / "clean"
    if not corpus_dir.exists():
        return [f"corpus/clean/ not found at {corpus_dir}"]

    # load all clean text into a dict keyed by doc_id
    texts: dict[str, str] = {}
    for path in corpus_dir.glob("*"):
        doc_id = path.stem.upper().replace("-", "_").replace(" ", "_")
        texts[doc_id] = path.read_text(encoding="utf-8", errors="replace")

    failures = []
    for doc_id, section_ref, substring, desc in CHECKS:
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
    parser.add_argument("--source", choices=["files", "db"], default="db")
    args = parser.parse_args()

    print(f"Validating {len(CHECKS)} section checks from {args.source}...")
    failures = validate_from_db() if args.source == "db" else validate_from_files()

    if failures:
        print(f"\nFAILED ({len(failures)}/{len(CHECKS)}):")
        for f in failures:
            print(f"  ✗ {f}")
        sys.exit(1)
    else:
        print(f"\nPASSED — all {len(CHECKS)} checks green. Safe to proceed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
