#!/usr/bin/env python3
"""
Scrape public SaaS help-center pages as STRUCTURAL SEED material for the support corpus.
Output is NOT ingested directly — it feeds gen_support_corpus.py which rewrites everything
into fictional "Acme Tasks" content.

Run:
  uv run python -m scripts.scrape_support_sources

Requires either:
  - FIRECRAWL_API_KEY  (preferred — markdown output, sitemap-aware)
  - falls back to plain HTTP fetch + readability (best-effort) when key absent

All output lands in demos/support/corpus/raw/_scrape_cache/{source}/{slug}.md.
This directory is gitignored — re-run is cheap.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

REPO_ROOT = Path(__file__).parent.parent.parent.parent
CACHE_ROOT = REPO_ROOT / "demos" / "support" / "corpus" / "raw" / "_scrape_cache"

# Curated topic list — each URL becomes a seed for one Acme Tasks doc.
# Picked across 6 real PM SaaS to keep tone/structure varied.
SOURCES: list[dict] = [
    # ── Linear ──
    {"source": "linear",  "slug": "billing-and-plans",     "url": "https://linear.app/docs/billing-and-plans"},
    {"source": "linear",  "slug": "saml-sso",              "url": "https://linear.app/docs/saml-sso"},
    {"source": "linear",  "slug": "api-rate-limits",       "url": "https://linear.app/docs/rate-limiting"},
    {"source": "linear",  "slug": "keyboard-shortcuts",    "url": "https://linear.app/docs/keyboard-shortcuts"},
    {"source": "linear",  "slug": "import",                "url": "https://linear.app/docs/import"},
    # ── Notion ──
    {"source": "notion",  "slug": "billing-faqs",          "url": "https://www.notion.so/help/billing-faqs"},
    {"source": "notion",  "slug": "change-your-plan",      "url": "https://www.notion.so/help/change-your-plan"},
    {"source": "notion",  "slug": "security-and-privacy",  "url": "https://www.notion.so/help/security-and-privacy"},
    {"source": "notion",  "slug": "two-step-verification", "url": "https://www.notion.so/help/two-step-verification"},
    {"source": "notion",  "slug": "exporting-content",     "url": "https://www.notion.so/help/exporting-content-from-notion"},
    # ── ClickUp ──
    {"source": "clickup", "slug": "subscription-billing",  "url": "https://help.clickup.com/hc/en-us/articles/6303515832855"},
    {"source": "clickup", "slug": "cancel-subscription",   "url": "https://help.clickup.com/hc/en-us/articles/6303528232855"},
    {"source": "clickup", "slug": "notifications",         "url": "https://help.clickup.com/hc/en-us/articles/6328422193943"},
    # ── Asana ──
    {"source": "asana",   "slug": "downgrade",             "url": "https://asana.com/guide/help/premium/downgrade"},
    {"source": "asana",   "slug": "sso-setup",             "url": "https://asana.com/guide/help/premium/sso"},
    {"source": "asana",   "slug": "data-export",           "url": "https://asana.com/guide/help/premium/csv-export"},
    {"source": "asana",   "slug": "project-templates",     "url": "https://asana.com/guide/help/projects/templates"},
    # ── Atlassian Jira ──
    {"source": "jira",    "slug": "pricing-and-licensing", "url": "https://support.atlassian.com/jira-software-cloud/docs/pricing-and-licensing/"},
    {"source": "jira",    "slug": "user-permissions",      "url": "https://support.atlassian.com/jira-cloud-administration/docs/configure-permissions/"},
    {"source": "jira",    "slug": "mobile-app",            "url": "https://support.atlassian.com/jira-cloud-mobile/docs/get-started-with-the-jira-cloud-mobile-app/"},
    # ── Slack (integrations / SSO chapters) ──
    {"source": "slack",   "slug": "sso-saml",              "url": "https://slack.com/help/articles/203772216-Set-up-SAML-based-SSO"},
    {"source": "slack",   "slug": "integrations",          "url": "https://slack.com/help/articles/115005265703-Manage-apps-on-Slack"},
    # ── Generic SLA references ──
    {"source": "atlassian-sla", "slug": "sla-overview",    "url": "https://www.atlassian.com/legal/sla"},
]


# ── Firecrawl client (preferred) ──────────────────────────────────────────────

def _firecrawl_fetch(url: str, api_key: str) -> str:
    """Fetch a single URL via Firecrawl → markdown."""
    resp = httpx.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
        timeout=60.0,
    )
    resp.raise_for_status()
    data = resp.json().get("data", {})
    return data.get("markdown", "")


# ── Fallback: plain HTTP + crude html-to-markdown ──────────────────────────────

def _strip_html(html: str) -> str:
    # Drop scripts / styles / nav junk.
    html = re.sub(r"<script\b[^>]*>.*?</script>",  "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style\b[^>]*>.*?</style>",    "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<nav\b[^>]*>.*?</nav>",        "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<footer\b[^>]*>.*?</footer>",  "", html, flags=re.DOTALL | re.IGNORECASE)
    # Headings → markdown
    for lvl in (1, 2, 3, 4):
        html = re.sub(rf"<h{lvl}\b[^>]*>(.*?)</h{lvl}>", lambda m, l=lvl: f"\n\n{'#'*l} {m.group(1).strip()}\n\n", html, flags=re.DOTALL | re.IGNORECASE)
    # Paragraphs + list items
    html = re.sub(r"<p\b[^>]*>(.*?)</p>",    r"\n\n\1\n\n", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<li\b[^>]*>(.*?)</li>",  r"\n- \1",     html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<br\s*/?>",              "\n",          html, flags=re.IGNORECASE)
    # Strip all remaining tags
    html = re.sub(r"<[^>]+>", "", html)
    # Decode common entities
    html = (html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"'))
    # Collapse whitespace
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def _http_fetch(url: str) -> str:
    resp = httpx.get(
        url,
        follow_redirects=True,
        timeout=30.0,
        headers={"User-Agent": "Mozilla/5.0 (compatible; acme-corpus-scraper/1.0)"},
    )
    resp.raise_for_status()
    return _strip_html(resp.text)


# ── Driver ────────────────────────────────────────────────────────────────────

def _write_cache(source: str, slug: str, url: str, content: str) -> Path:
    out_dir = CACHE_ROOT / source
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}.md"
    header = f"---\nsource_url: {url}\nsource_site: {source}\nscraped_at_iso: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n---\n\n"
    out_path.write_text(header + content, encoding="utf-8")
    return out_path


def main() -> int:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)

    firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")
    if firecrawl_key:
        print("Using Firecrawl (FIRECRAWL_API_KEY set).")
        fetcher = lambda u: _firecrawl_fetch(u, firecrawl_key)  # noqa: E731
    else:
        print("FIRECRAWL_API_KEY not set — falling back to plain HTTP fetch (lower quality).")
        fetcher = _http_fetch

    successes = []
    failures = []
    for entry in SOURCES:
        url = entry["url"]
        source = entry["source"]
        slug = entry["slug"]
        print(f"\n[{source}/{slug}] {url}")
        try:
            content = fetcher(url)
            if not content or len(content) < 200:
                raise RuntimeError(f"empty / too-short result ({len(content)} chars)")
            out = _write_cache(source, slug, url, content)
            print(f"  → {out.relative_to(REPO_ROOT)}  ({len(content)} chars)")
            successes.append(entry)
        except Exception as e:
            print(f"  ! failed: {e}")
            failures.append({"entry": entry, "error": str(e)})
        time.sleep(1)  # be polite

    # Summary manifest — gen_support_corpus.py reads this to know what's cached.
    summary = {
        "successes": successes,
        "failures": failures,
        "total_attempted": len(SOURCES),
    }
    (CACHE_ROOT / "_summary.json").write_text(json.dumps(summary, indent=2))

    print(f"\nDone. {len(successes)}/{len(SOURCES)} succeeded → {CACHE_ROOT}")
    if failures:
        print(f"  {len(failures)} failed (see _summary.json).")
        # Non-fatal: gen step works with whatever is cached.
    return 0


if __name__ == "__main__":
    sys.exit(main())
