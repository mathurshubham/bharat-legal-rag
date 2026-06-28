# Bharat Legal RAG — Raspberry Pi Deployment Guide

Target machine: Raspberry Pi 4 (4 GB RAM), running Debian aarch64.  
Hostnames: `rag.shubhammathur.in` (web) · `rag-api.shubhammathur.in` (API)

---

## Port map

| Service  | Port | Notes                              |
|----------|------|------------------------------------|
| ParadeDB | 5435 | Docker container                   |
| FastAPI  | 8000 | Bare-metal (see why below)         |
| Next.js  | 3002 | Bare-metal standalone              |

Ports already taken by other services on this Pi: 3000 (Sentinel), 3001 (ai-dlp-proxy), 3005/3006 (Social Agent), 5000/5001 (PDM), 5433/5434 (other Postgres instances), 5500 (HireStar), 8900 (SearXNG).

> **Why bare-metal for API and web?**  
> Building Docker images for api/web on the Pi 4 (4 GB) causes OOM during compilation — torch + Next.js together exhaust available memory. The DB runs in Docker because ParadeDB is a pre-built image (no build step). API and web run as nohup processes instead.

---

## Prerequisites (one-time, already done)

These are already set up on the Pi. Skip unless rebuilding from scratch.

```bash
# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc

# pnpm
npm install -g pnpm

# Python 3.12 venv
cd ~/Documents/projects/bharat-legal-rag/apps/api
uv venv --python 3.12 .venv
uv pip install -e .

# Next.js production build
cd ~/Documents/projects/bharat-legal-rag/apps/web
pnpm install
pnpm build
# Copy static assets into standalone bundle
cp -r .next/static .next/standalone/.next/static
cp -r public .next/standalone/public 2>/dev/null || true
```

---

## Deployment (run after every `git pull`)

### 1. Pull latest code

```bash
cd ~/Documents/projects/bharat-legal-rag
git pull
```

### 2. Check the .env file

The `.env` file must exist at the repo root with these values (do NOT commit it — it contains secrets):

```
OPENROUTER_API_KEY=sk-or-v1-...        # required — prevents 1.2 GB local model download
DATABASE_URL=postgresql://legal:legal@localhost:5435/legalrag
NEXT_PUBLIC_API_URL=https://rag-api.shubhammathur.in
CORS_ORIGINS=http://localhost:3002,https://rag.shubhammathur.in

POSTGRES_USER=legal
POSTGRES_PASSWORD=legal
POSTGRES_DB=legalrag

GEN_MODEL=anthropic/claude-sonnet-4-5
HYDE_MODEL=openai/gpt-4.1-mini
RERANKER_MODEL=rerank-v3.5
EMBED_MODEL=nvidia/llama-nemotron-embed-vl-1b-v2:free
```

There must also be a symlink so the API process (which runs from `apps/api/`) can find the repo root `.env`:

```bash
# One-time setup — already done on this Pi:
ln -s ../../.env ~/Documents/projects/bharat-legal-rag/apps/api/.env
```

Without this symlink `CORS_ORIGINS` is never loaded and the browser is blocked from calling the API, causing the demo picker to fall back to `/law`.

There must also be `apps/web/.env.local` with:

```
NEXT_PUBLIC_API_URL=https://rag-api.shubhammathur.in
```

This is needed because Next.js only reads `.env` from its own directory (`apps/web/`), not the repo root. `NEXT_PUBLIC_*` vars are baked into the JS bundle at build time — if this file is missing, the browser will try to reach `localhost:8000` (its own machine) instead of the API tunnel.

### 3. Start ParadeDB

```bash
# If the container already exists (normal case — just restart it):
sudo docker start bharat-legal-rag-db-1

# If it doesn't exist yet (first deploy):
sudo docker compose -f ~/Documents/projects/bharat-legal-rag/docker-compose.yml up db -d

# Wait until healthy:
until sudo docker exec bharat-legal-rag-db-1 pg_isready -U legal -d legalrag 2>/dev/null; do sleep 2; done && echo "DB ready"
```

### 4. Restore the DB dump (first deploy only)

Skip this step if the database already has data.

> **How the dump was created (2026-06-28):** Dumped from local Docker container on Mac (macOS), transferred to Pi via SCP over SSH.
>
> ```bash
> # On Mac — dump from local Docker container:
> docker exec legal-rag-db-1 pg_dump -U legal -d legalrag -Fc -f /tmp/legalrag.dump
> docker cp legal-rag-db-1:/tmp/legalrag.dump ./legalrag.dump
>
> # Transfer to Pi (pubkey auth — run ssh-copy-id first if not done):
> scp -i ~/.ssh/id_ed25519 ./legalrag.dump \
>   rpism@192.168.1.22:/home/rpism/Documents/projects/bharat-legal-rag/legalrag.dump
> ```

```bash
# Verify row count first — if this returns 4896 total, skip the restore:
sudo docker exec bharat-legal-rag-db-1 psql -U legal -d legalrag \
  -c "SELECT doc_id, count(*) FROM chunks GROUP BY doc_id ORDER BY doc_id;"

# Restore (data-section only to avoid duplicate-index errors):
sudo docker exec -i bharat-legal-rag-db-1 \
  pg_restore -U legal -d legalrag -Fc --section=data \
  < ~/Documents/projects/bharat-legal-rag/legalrag.dump

# Recreate indexes (BM25 + HNSW):
sudo docker exec bharat-legal-rag-db-1 psql -U legal -d legalrag -c "
  CREATE INDEX IF NOT EXISTS chunks_hnsw ON chunks USING hnsw (embedding vector_cosine_ops);
  CREATE INDEX IF NOT EXISTS chunks_bm25 ON chunks USING bm25 (id, content, doc_title, section_ref) WITH (key_field='id');
  CREATE INDEX IF NOT EXISTS chunks_doc_id ON chunks (doc_id);
  CREATE INDEX IF NOT EXISTS chunks_section_ref ON chunks (doc_id, section_ref);
"
```

Expected counts after restore:

| doc_id                   | count |
|--------------------------|-------|
| BNS_2023                 | 767   |
| BNSS_2023                | 1233  |
| BSA_2023                 | 362   |
| CONSTITUTION             | 1782  |
| CONSUMER_PROTECTION_2019 | 129   |
| CONTRACT_ACT_1872        | 516   |
| DPDP_2023                | 104   |
| LAW_MAPPINGS             | 3     |
| **Total**                | **4896** |

### 5. Stop the API and web services

```bash
sudo systemctl stop bharat-legal-api bharat-legal-web
sleep 2
# Confirm ports are free:
ss -tlnp | grep -E "8000|3002" || echo "ports free"
```

### 6. Rebuild Python dependencies (only if pyproject.toml changed)

```bash
cd ~/Documents/projects/bharat-legal-rag/apps/api
uv pip install -e . 2>&1 | tail -5
```

Skip if only Python source files changed — the venv stays valid.

### 7. Rebuild the Next.js bundle (only if web code or .env.local changed)

```bash
cd ~/Documents/projects/bharat-legal-rag/apps/web
pnpm install         # only needed if package.json changed
pnpm build
# Copy static assets into standalone:
cp -r .next/static .next/standalone/.next/static
cp -r public .next/standalone/public 2>/dev/null || true
```

Skip if only API code changed.

### 8. Start the API

```bash
sudo systemctl start bharat-legal-api
sleep 10 && curl -s http://localhost:8000/api/health
# Expected: {"status":"ok"}
```

### 9. Start the web server

```bash
sudo systemctl start bharat-legal-web
sleep 5 && curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:3002
# Expected: HTTP 200
```

### 10. Verify everything

```bash
# Local health checks:
curl -s http://localhost:8000/api/health
curl -s -o /dev/null -w "Web HTTP %{http_code}\n" http://localhost:3002

# Tunnel health checks:
curl -s https://rag-api.shubhammathur.in/api/health
curl -s -o /dev/null -w "Tunnel web HTTP %{http_code}\n" https://rag.shubhammathur.in

# Memory (should have >500 MB available):
free -h

# DB row count:
sudo docker exec bharat-legal-rag-db-1 psql -U legal -d legalrag \
  -c "SELECT count(*) FROM chunks;"
# Expected: 5574
```

---

## After a Pi reboot

All three services restart automatically on reboot via their respective init systems:

| Service  | Init system | Unit / config                                                  |
|----------|-------------|----------------------------------------------------------------|
| ParadeDB | Docker       | `restart: unless-stopped` in `docker-compose.yml`             |
| FastAPI  | systemd      | `/etc/systemd/system/bharat-legal-api.service` (enabled)      |
| Next.js  | systemd      | `/etc/systemd/system/bharat-legal-web.service` (enabled)      |

The API service waits for the DB to be healthy before starting (`ExecStartPre` polls `pg_isready`), so ordering is guaranteed.

To verify after a reboot:

```bash
sudo systemctl status bharat-legal-api bharat-legal-web
curl -s http://localhost:8000/api/health
curl -s -o /dev/null -w "Web HTTP %{http_code}\n" http://localhost:3002
```

To view logs:

```bash
sudo journalctl -u bharat-legal-api -f
sudo journalctl -u bharat-legal-web -f
```

---

## Cloudflare tunnel

The tunnel is managed by systemd (`cloudflared`) and survives reboots automatically. DNS CNAMEs for both hostnames already point to tunnel ID `48dbebde-3a88-419e-b043-0ca5b71f8af1`.

Config: `/etc/cloudflared/config.yml`

If you need to add or change hostnames:

```bash
# Add DNS record:
cloudflared tunnel route dns 48dbebde-3a88-419e-b043-0ca5b71f8af1 <new-hostname>

# Restart tunnel after config change:
sudo systemctl restart cloudflared
sudo journalctl -u cloudflared -n 20 --no-pager
```

---

## Troubleshooting

### "Failed to fetch" in the browser
The most likely cause is `NEXT_PUBLIC_API_URL` was baked incorrectly into the JS bundle at build time.

```bash
# Check what URL is baked into the live bundle:
curl -s http://localhost:3002 | grep -o 'src="[^"]*\.js"' | head -5
# Pick the last .js chunk file, then:
grep -o 'indialegal-rag-api[^"]*\|localhost:8000' \
  apps/web/.next/standalone/.next/static/chunks/<chunk>.js | head -3
```

If it shows `localhost:8000`, the `.env.local` was missing when `pnpm build` ran. Fix:

```bash
echo "NEXT_PUBLIC_API_URL=https://rag-api.shubhammathur.in" > apps/web/.env.local
cd apps/web && pnpm build
cp -r .next/static .next/standalone/.next/static
# Restart the web server (step 9 above)
```

### CORS errors in browser console
The API's allowed origins are in `apps/api/app/main.py`. If you add a new web hostname, add it there and restart the API.

### API log
```bash
sudo journalctl -u bharat-legal-api -f
```

### Web log
```bash
sudo journalctl -u bharat-legal-web -f
```

### Port already in use
```bash
# Find what's holding a port:
sudo ss -tlnp | grep <port>
# Kill it by PID:
kill -9 <pid>
```

### OOM / Pi crashes during docker build
Do NOT run `sudo docker compose build api web` in parallel on this Pi — it will OOM. If you ever need to build Docker images for api/web:
1. Build one at a time: `sudo docker compose build api` first, wait, then `sudo docker compose build web`
2. Monitor memory: `watch -n2 free -h`
3. Close other memory-heavy processes first
