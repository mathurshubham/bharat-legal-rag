#!/usr/bin/env bash
#
# Gate-0 probe 2 — pg_search fused-predicate verification.
#
# Question this answers (and nothing else):
#     When we add `AND demo_id = 'law'` to a BM25 query, does pg_search use the
#     BM25 index for the fused predicate, or does it fall back to a sequential
#     scan / post-filter after the BM25 match?
#
# Why it matters:
#     The build plan's single-index design (init.sql adds demo_id to the BM25
#     index columns) is only correct if the fused predicate is one index walk.
#     If pg_search post-filters, the _bm25 query in step 0.3 must change shape
#     (two-step: BM25 candidate set -> SQL/app post-filter), and you must measure
#     top-k recall impact on the 25 Law CHECKS before committing. This probe
#     decides which path. The retrieval read-side rewrite (0.3) cannot start
#     until this is answered.
#
# What it does:
#     Against a THROWAWAY copy of the DB (restored from legalrag.dump), it adds a
#     sentinel demo_id column, builds a BM25 index that INCLUDES demo_id, and runs
#     EXPLAIN ANALYZE on the fused predicate. It then greps the plan for the BM25
#     index name vs a Seq Scan / Filter line so the answer is unambiguous.
#
# Usage:
#     ./check_pg_search_fusion.sh "postgresql://user:pass@localhost:5435/legalrag_probe"
#
#     Set up the throwaway DB first (do NOT run against your real DB):
#       createdb legalrag_probe
#       pg_restore -d legalrag_probe legalrag.dump   # or psql < legalrag.sql
#
# Read the output:
#     - If the plan shows the BM25 index (e.g. "chunks_bm25") driving the scan and
#       NO separate "Filter: (demo_id = ...)" doing the heavy lifting -> FUSED.
#       Proceed with the single-index design in init.sql 0.1.
#     - If the plan shows a Seq Scan on chunks, or a Filter removing most rows
#       AFTER a broad BM25 match -> NOT FUSED. Switch _bm25 to the two-step shape
#       and measure recall against the 25 Law CHECKS.

set -euo pipefail

DB_URL="${1:?Usage: check_pg_search_fusion.sh <throwaway_db_url>}"

echo "Probing: ${DB_URL}"
echo "NOTE: run this against a THROWAWAY restore of legalrag.dump, never prod."
echo

# 1) Add a sentinel demo_id (idempotent), backfill, and build a BM25 index that
#    includes demo_id in its column list — mirroring the proposed init.sql.
psql "${DB_URL}" -v ON_ERROR_STOP=1 <<'SQL'
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS demo_id TEXT;
UPDATE chunks SET demo_id = 'law' WHERE demo_id IS NULL;
-- Add a second sentinel tenant so the planner has a reason to filter.
-- Duplicate a small slice under demo_id='other' to make demo_id selective.
INSERT INTO chunks (doc_id, doc_title, section_ref, chunk_index, content, tokens, embedding, embed_manifest, embed_model, demo_id)
SELECT doc_id, doc_title, section_ref, chunk_index, content, tokens, embedding, embed_manifest, embed_model, 'other'
FROM chunks WHERE demo_id = 'law' LIMIT 200;

DROP INDEX IF EXISTS chunks_bm25_probe;
CREATE INDEX chunks_bm25_probe ON chunks
  USING bm25 (id, content, doc_title, section_ref, demo_id)
  WITH (key_field='id');
ANALYZE chunks;
SQL

echo "----- EXPLAIN ANALYZE: fused BM25 + demo_id predicate -----"
PLAN="$(psql "${DB_URL}" -v ON_ERROR_STOP=1 -At <<'SQL'
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT id FROM chunks
WHERE content @@@ 'murder' AND demo_id = 'law'
LIMIT 20;
SQL
)"
echo "${PLAN}"
echo "-----------------------------------------------------------"
echo

# 2) Verdict heuristics.
if echo "${PLAN}" | grep -qiE 'chunks_bm25_probe|bm25'; then
  if echo "${PLAN}" | grep -qiE 'Seq Scan on chunks'; then
    echo "VERDICT: AMBIGUOUS — BM25 index referenced but a Seq Scan is also present."
    echo "         Inspect the plan by hand: is demo_id applied at the index or as a"
    echo "         post-Filter? If post-Filter on a broad match -> treat as NOT FUSED."
    exit 1
  fi
  if echo "${PLAN}" | grep -qiE 'Filter: .*demo_id'; then
    echo "VERDICT: LIKELY NOT FUSED — demo_id appears as a post-match Filter, not an"
    echo "         index-level predicate. Use the two-step _bm25 shape in 0.3 and"
    echo "         measure recall against the 25 Law CHECKS before committing."
    exit 1
  fi
  echo "VERDICT: FUSED — the BM25 index drives the scan and demo_id is applied at the"
  echo "         index, no heavy post-filter. Proceed with the single-index init.sql (0.1)."
  exit 0
fi

if echo "${PLAN}" | grep -qiE 'Seq Scan on chunks'; then
  echo "VERDICT: NOT FUSED — planner chose a Seq Scan; the BM25 index isn't being used"
  echo "         for the fused predicate. Use the two-step _bm25 shape in 0.3."
  exit 1
fi

echo "VERDICT: UNCLEAR — neither the BM25 index nor a Seq Scan matched the expected"
echo "         strings. Read the plan above manually before deciding 0.3's SQL shape."
exit 1
