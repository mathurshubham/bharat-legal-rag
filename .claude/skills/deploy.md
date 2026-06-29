# deploy

Deploy the Bharat Legal RAG stack on this Raspberry Pi.

## When to use

Use this skill when the user asks to deploy, redeploy, restart services, or pull and deploy changes.

## Instructions

You are running on the Raspberry Pi that hosts this project. Follow these steps:

### 1. Pull latest code

```bash
cd ~/Documents/projects/bharat-legal-rag
git pull
```

Note the changed files — use `git diff --name-only HEAD@{1} HEAD` after pulling.

### 2. Detect what needs rebuilding

- Changes under `apps/api/` or `pyproject.toml` → rebuild Python deps (step 5)
- Changes under `apps/web/` → rebuild Next.js bundle (step 6)
- Only docs/config changed → skip both rebuilds and proceed to restart

### 3. Ensure DB is running

```bash
sudo docker inspect --format='{{.State.Status}}' bharat-legal-rag-db-1
# If not running:
sudo docker start bharat-legal-rag-db-1
until sudo docker exec bharat-legal-rag-db-1 pg_isready -U legal -d legalrag 2>/dev/null; do sleep 2; done
```

### 4. Stop API and web

```bash
sudo systemctl stop bharat-legal-api bharat-legal-web
sleep 2
ss -tlnp | grep -E "8000|3002" || echo "ports free"
```

### 5. Rebuild Python deps (only if API code changed)

```bash
cd ~/Documents/projects/bharat-legal-rag/apps/api
uv pip install -e . 2>&1 | tail -5
```

### 6. Rebuild Next.js bundle (only if web code changed)

```bash
cd ~/Documents/projects/bharat-legal-rag/apps/web
pnpm install  # only if package.json changed
pnpm build
cp -r .next/static .next/standalone/.next/static
cp -r public .next/standalone/public 2>/dev/null || true
```

### 7. Start API and verify

```bash
sudo systemctl start bharat-legal-api
# Wait up to 30s for health:
for i in $(seq 1 15); do
  curl -s http://localhost:8000/api/health | grep -q '"ok"' && echo "API healthy" && break
  sleep 2
done
```

### 8. Start web and verify

```bash
sudo systemctl start bharat-legal-web
sleep 5
curl -s -o /dev/null -w "Web HTTP %{http_code}\n" http://localhost:3002
```

### 9. Final health check

```bash
curl -s http://localhost:8000/api/health
curl -s -o /dev/null -w "Web HTTP %{http_code}\n" http://localhost:3002
curl -s https://rag-api.shubhammathur.in/api/health
curl -s -o /dev/null -w "Tunnel web HTTP %{http_code}\n" https://rag.shubhammathur.in
free -h
```

Report: what changed, what was rebuilt, health check results, and memory available.

## Flags for deploy.sh

The script at `scripts/deploy.sh` accepts:
- `--force-rebuild-api` — rebuild Python deps even if no API files changed
- `--force-rebuild-web` — rebuild Next.js even if no web files changed  
- `--skip-db` — skip DB container check

## Notes

- Do NOT run Docker builds for api/web — OOM risk on Pi 4 (4 GB RAM)
- Never wipe the DB — always merge (see DEPLOY.md §4)
- Ports 8000 (API) and 3002 (web) must be free before starting services
