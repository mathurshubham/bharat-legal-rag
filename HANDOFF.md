# Handoff — Pi Deployment + Demo Multi-tenancy

Branch: `deploy/pi-infra-and-demo-multitenancy`  
Date: 2026-06-25  
Author: Shubham Mathur

---

## What was being done

Two parallel tracks of work were in progress:

### Track 1 — Raspberry Pi production deployment

The app is being deployed bare-metal on a Raspberry Pi 4 (4 GB RAM) at:
- Web: `https://indialegal-rag.shubhammathur.in`
- API: `https://indialegal-rag-api.shubhammathur.in`

Both are exposed via a Cloudflare tunnel (tunnel ID `48dbebde-3a88-419e-b043-0ca5b71f8af1`). ParadeDB runs in Docker; API (FastAPI/uvicorn) and web (Next.js standalone) run as bare-metal `nohup` processes because building Docker images for both on the Pi 4 causes OOM during compilation.

Changes shipped as part of this track:

| File | What changed |
|------|-------------|
| `apps/api/Dockerfile` | Python 3.11 → 3.12; added `/api/health` HEALTHCHECK |
| `apps/api/app/main.py` | Added `http://localhost:3002` and the production tunnel domain to CORS allowed origins |
| `apps/web/Dockerfile` | Bypassed pnpm v10 `minimumReleaseAge` policy; added `ARG/ENV NEXT_PUBLIC_API_URL` so the API URL is baked into the JS bundle at build time |
| `apps/web/package.json` | `next start` → `next start --port 3002` (was binding to wrong port in prod) |
| `docker-compose.yml` | Added `restart: unless-stopped` to all services; moved `NEXT_PUBLIC_API_URL` from runtime env to build arg; removed `./corpus` and `./apps/api/app/prompts` volume mounts from api service (these were dev-only mounts no longer needed) |
| `apps/api/.dockerignore` | New — excludes `.venv`, `__pycache__`, `.pyc`, `.env*`, `*.log` |
| `apps/web/.dockerignore` | New — excludes `node_modules`, `.next`, `.env*`, `*.log` |
| `DEPLOY.md` | New — full step-by-step Pi deployment guide (already pushed to main) |

### Track 2 — Demo multi-tenancy (schema prepared, API not yet wired)

The system needs to support multiple isolated "demo" tenants sharing the same database. Each demo has its own scoped corpus so queries only retrieve from its own documents.

The DB schema has been updated (`apps/api/scripts/init.sql`) to add:

```sql
demo_id TEXT NOT NULL   -- new column on chunks table
```

The BM25 and composite lookup indexes have been updated to include `demo_id` so a `WHERE demo_id = :demo` clause fuses into the index walk (no post-scan cost). The old `chunks_doc_id` and `chunks_section_ref` indexes have been replaced with `chunks_demo_doc` and `chunks_demo_section` which are prefixed by `demo_id`.

**This schema change is not yet live** — the existing Pi database was dumped before this column was added. The API (`query.py`, `retrieval.py`) does not yet read or pass `demo_id`.

---

## What still needs to be done

### 1. Wire `demo_id` into the API (the main remaining task)

The schema is ready. The API needs to:

- **`apps/api/app/retrieval.py`** — All three SQL queries (`_dense`, `_bm25`, and the HyDE dense path) need a `WHERE demo_id = %s` clause added. The `retrieve()` function signature needs a `demo_id: str` parameter which gets threaded into each query.

- **`apps/api/app/query.py`** — The `/api/query` endpoint needs a `demo_id: str` query param (or header) and must pass it through to `retrieve()`.

- The `demo_id` value can start as a simple query param (e.g. `?demo_id=default`) with `"default"` as the fallback to keep the existing single-tenant behavior working.

### 2. Re-ingest the corpus with `demo_id`

The existing DB dump was created before the `demo_id` column was added. The migration path:

**Option A (preferred — fresh schema):**
```bash
# Drop and recreate the DB, then re-ingest
sudo docker exec bharat-legal-rag-db-1 psql -U legal -d legalrag -c "DROP TABLE IF EXISTS chunks CASCADE;"
# Re-run init.sql (happens automatically on next `docker compose up db`)
# Then re-run the ingest script with demo_id="default" for all existing documents
```

**Option B (in-place migration):**
```bash
sudo docker exec bharat-legal-rag-db-1 psql -U legal -d legalrag -c "
  ALTER TABLE chunks ADD COLUMN IF NOT EXISTS demo_id TEXT NOT NULL DEFAULT 'default';
  DROP INDEX IF EXISTS chunks_doc_id;
  DROP INDEX IF EXISTS chunks_section_ref;
  CREATE INDEX IF NOT EXISTS chunks_demo_doc ON chunks (demo_id, doc_id);
  CREATE INDEX IF NOT EXISTS chunks_demo_section ON chunks (demo_id, doc_id, section_ref);
"
# Then rebuild BM25 index to include demo_id:
# Note: BM25 indexes cannot be ALTER'd — must drop and recreate
sudo docker exec bharat-legal-rag-db-1 psql -U legal -d legalrag -c "
  DROP INDEX IF EXISTS chunks_bm25;
  CREATE INDEX chunks_bm25 ON chunks
    USING bm25 (id, content, doc_title, section_ref, demo_id)
    WITH (key_field='id');
"
```

Option B is faster (no re-ingest). The HNSW index can stay as-is — it doesn't need `demo_id`.

### 3. Update the ingest script

The ingest script (wherever it lives — not in this repo) needs to write `demo_id` when inserting chunks. For the existing documents, use `demo_id = "default"`.

### 4. Frontend — pass `demo_id`

Once the API accepts `demo_id`, the web UI should pass it. For now a hardcoded `?demo_id=default` on all fetch calls is fine. A proper demo switcher can come later.

### 5. Verify the Pi deploy end-to-end

After the API changes are wired:
```bash
# On the Pi — full smoke test:
curl -s https://indialegal-rag-api.shubhammathur.in/api/health
# Then a real query via the tunnel UI at https://indialegal-rag.shubhammathur.in
```

---

## Current system state on the Pi

- ParadeDB: running in Docker at port 5435, `restart: unless-stopped` (survives reboots)
- API: bare-metal uvicorn at port 8000, must be manually restarted after reboots (see `DEPLOY.md § After a Pi reboot`)
- Web: bare-metal Next.js standalone at port 3002, same
- DB: has 4896 chunks across 8 documents (pre-`demo_id` schema — needs migration per above)
- Cloudflare tunnel: managed by systemd `cloudflared`, survives reboots automatically

## Key files to read

| File | Purpose |
|------|---------|
| `DEPLOY.md` | Full Pi deployment runbook |
| `apps/api/app/retrieval.py` | Where `demo_id` WHERE clauses need to be added |
| `apps/api/app/query.py` | Where `demo_id` param needs to be added to the endpoint |
| `apps/api/scripts/init.sql` | Updated schema — source of truth for the new indexes |
| `.env` (repo root, not committed) | Contains `OPENROUTER_API_KEY`, `DATABASE_URL`, model names |
| `apps/web/.env.local` (not committed) | Contains `NEXT_PUBLIC_API_URL` for web build |
