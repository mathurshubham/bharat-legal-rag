#!/usr/bin/env python3
"""
Gate-0 probe 1 — embedding asymmetry check.

Question this answers (and nothing else):
    Does the chosen OpenRouter embedding model actually produce DIFFERENT vectors
    for the same text depending on input_type=passage vs input_type=query?

Why it matters:
    OpenRouter-fronted embedding endpoints sometimes silently ignore an input_type
    they don't recognise and return identical vectors. If that happens, the
    embed_doc/embed_query split in apps/api/app/embed.py is a no-op and retrieval
    silently degrades across every demo. This is the highest-risk unverified claim
    in the build plan, so it gates Phase 0.

Exit codes:
    0  -> asymmetry confirmed via input_type. Ship bge-m3 as planned.
    2  -> input_type ignored (vectors identical). Manual-prefix fallback was tried:
          if --try-prefix made them differ, you may ship WITH MANUAL PREFIXES
          (read the printed framing carefully — this is "asymmetry via input
          divergence", not "the parameter now works"). If even prefixes don't
          differ, switch model (Option B: qwen3-embedding-8b).
    3  -> API / config error (couldn't even get two vectors to compare).

Usage:
    export OPENROUTER_API_KEY=sk-or-...
    python check_embed_asymmetry.py --model baai/bge-m3
    python check_embed_asymmetry.py --model baai/bge-m3 --try-prefix
    # optional: route through the Cloudflare AI Gateway exactly like prod
    python check_embed_asymmetry.py --model baai/bge-m3 \
        --cf-account-id $CF_ACCOUNT_ID --cf-gateway-id $CF_GATEWAY_ID

No third-party deps (uses urllib + math) so it runs anywhere the repo's venv exists.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.request
import urllib.error

# A sentence with both lexical and semantic content; same text both ways.
PROBE_TEXT = "What is the punishment for murder under the law?"

# bge-m3 was trained with an explicit retrieval instruction on the QUERY side.
# This is the manual-prefix fallback (Option A in the plan).
QUERY_PREFIX = "Represent this query for retrieving relevant passages: "

IDENTICAL_THRESHOLD = 0.9999  # >= this means "effectively identical" => param ignored


def _endpoint(cf_account_id: str | None, cf_gateway_id: str | None) -> str:
    if cf_account_id and cf_gateway_id:
        # Mirror the prod path: CF AI Gateway -> OpenRouter, OpenAI-compatible.
        return (
            f"https://gateway.ai.cloudflare.com/v1/{cf_account_id}/{cf_gateway_id}"
            f"/openrouter/v1/embeddings"
        )
    return "https://openrouter.ai/api/v1/embeddings"


def embed(text: str, *, model: str, input_type: str, key: str, url: str) -> list[float]:
    """One embedding call. input_type is sent the way the existing embed.py sends it."""
    body = json.dumps(
        {"model": model, "input": text, "input_type": input_type, "dimensions": 1024}
    ).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "rag-demos",
            "X-Title": "rag-demos",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"HTTP {e.code} for input_type={input_type}: {e.read().decode()[:400]}\n")
        sys.exit(3)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"Request failed for input_type={input_type}: {e}\n")
        sys.exit(3)

    try:
        vec = payload["data"][0]["embedding"]
    except (KeyError, IndexError, TypeError):
        sys.stderr.write(f"Unexpected response shape: {json.dumps(payload)[:400]}\n")
        sys.exit(3)

    if len(vec) != 1024:
        sys.stderr.write(
            f"WARNING: returned dim={len(vec)}, expected 1024. "
            f"This contradicts the locked schema vector(1024) — STOP and re-check Gate 0.\n"
        )
        sys.exit(3)
    return vec


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="baai/bge-m3")
    ap.add_argument("--try-prefix", action="store_true",
                    help="If input_type is ignored, retry with a manual query prefix (Option A).")
    ap.add_argument("--cf-account-id", default=os.getenv("CF_ACCOUNT_ID"))
    ap.add_argument("--cf-gateway-id", default=os.getenv("CF_GATEWAY_ID"))
    args = ap.parse_args()

    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        sys.stderr.write("OPENROUTER_API_KEY not set.\n")
        sys.exit(3)

    url = _endpoint(args.cf_account_id, args.cf_gateway_id)
    print(f"Model: {args.model}")
    print(f"Endpoint: {url}")
    print(f"Probe text: {PROBE_TEXT!r}\n")

    v_passage = embed(PROBE_TEXT, model=args.model, input_type="passage", key=key, url=url)
    v_query = embed(PROBE_TEXT, model=args.model, input_type="query", key=key, url=url)

    sim = cosine(v_passage, v_query)
    print(f"cosine(passage, query) via input_type = {sim:.6f}")

    if sim < IDENTICAL_THRESHOLD:
        print("\nPASS — input_type produces measurably different vectors.")
        print("bge-m3 honors the parameter; embed_doc/embed_query split is real. Ship as planned.")
        sys.exit(0)

    print("\nFAIL — vectors are effectively identical: input_type is being IGNORED.")

    if not args.try_prefix:
        print("Re-run with --try-prefix to test the manual-prefix fallback (Option A).")
        sys.exit(2)

    print("\nTrying Option A: manual query prefix on the query side only...")
    v_query_prefixed = embed(QUERY_PREFIX + PROBE_TEXT, model=args.model,
                             input_type="query", key=key, url=url)
    sim_prefixed = cosine(v_passage, v_query_prefixed)
    print(f"cosine(passage, PREFIXED query) = {sim_prefixed:.6f}")

    if sim_prefixed < IDENTICAL_THRESHOLD:
        print("\nOption A WORKS — but read this framing carefully:")
        print("  The vectors differ because the INPUT TEXT differs (prefix added),")
        print("  NOT because the input_type parameter is now honored. This is a")
        print("  legitimate fix — bge-m3 was trained for exactly this prefix pattern —")
        print("  but in embed.py, implement embed_query() to PREPEND THE PREFIX, and do")
        print("  NOT rely on input_type. Document the mechanism so future debugging is honest.")
        print("\n  ACTION: ship bge-m3 with manual query prefix in embed_query().")
        sys.exit(2)

    print("\nOption A FAILED too — prefix made no difference.")
    print("  ACTION: Option B — switch to qwen3-embedding-8b (1024-dim Matryoshka),")
    print("  one env-var change (EMBED_MODEL). Re-run this probe against it.")
    sys.exit(2)


if __name__ == "__main__":
    main()
