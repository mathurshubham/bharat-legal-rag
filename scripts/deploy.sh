#!/usr/bin/env bash
# Bharat Legal RAG — deployment script
# Usage: ./scripts/deploy.sh [--force-rebuild-api] [--force-rebuild-web] [--skip-db]
# See DEPLOY.md for full reference.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$REPO_DIR/apps/api"
WEB_DIR="$REPO_DIR/apps/web"

FORCE_REBUILD_API=false
FORCE_REBUILD_WEB=false
SKIP_DB=false

for arg in "$@"; do
  case $arg in
    --force-rebuild-api) FORCE_REBUILD_API=true ;;
    --force-rebuild-web) FORCE_REBUILD_WEB=true ;;
    --skip-db)           SKIP_DB=true ;;
  esac
done

log() { echo "[deploy] $*"; }
ok()  { echo "[deploy] ✓ $*"; }
err() { echo "[deploy] ✗ $*" >&2; exit 1; }

# ── 1. Pull ──────────────────────────────────────────────────────────────────

log "Pulling latest from origin/main..."
cd "$REPO_DIR"
git pull

# Detect what changed since the previous HEAD
PREV_HEAD=$(git rev-parse HEAD@{1} 2>/dev/null || git rev-parse HEAD)
CHANGED=$(git diff --name-only "$PREV_HEAD" HEAD 2>/dev/null || true)

log "Changed files:"
echo "$CHANGED" | sed 's/^/  /'

NEEDS_API_REBUILD=false
NEEDS_WEB_REBUILD=false

echo "$CHANGED" | grep -qE '^apps/api/|^pyproject\.toml' && NEEDS_API_REBUILD=true || true
echo "$CHANGED" | grep -qE '^apps/web/'                  && NEEDS_WEB_REBUILD=true  || true

$FORCE_REBUILD_API && NEEDS_API_REBUILD=true
$FORCE_REBUILD_WEB && NEEDS_WEB_REBUILD=true

# ── 2. DB ────────────────────────────────────────────────────────────────────

if ! $SKIP_DB; then
  log "Ensuring ParadeDB container is running..."
  if sudo docker inspect --format='{{.State.Status}}' bharat-legal-rag-db-1 2>/dev/null | grep -q running; then
    ok "DB already running"
  else
    sudo docker start bharat-legal-rag-db-1
    log "Waiting for DB to be ready..."
    until sudo docker exec bharat-legal-rag-db-1 pg_isready -U legal -d legalrag 2>/dev/null; do sleep 2; done
    ok "DB ready"
  fi
fi

# ── 3. Stop services ─────────────────────────────────────────────────────────

log "Stopping API and web services..."
sudo systemctl stop bharat-legal-api bharat-legal-web 2>/dev/null || true
sleep 2
ss -tlnp | grep -E "8000|3002" && err "Ports still in use after stop" || ok "Ports free"

# ── 4. Rebuild Python deps ───────────────────────────────────────────────────

if $NEEDS_API_REBUILD; then
  log "Rebuilding Python dependencies..."
  cd "$API_DIR"
  uv pip install -e . 2>&1 | tail -5
  ok "Python deps updated"
else
  log "No API changes — skipping Python dep rebuild"
fi

# ── 5. Rebuild Next.js ───────────────────────────────────────────────────────

if $NEEDS_WEB_REBUILD; then
  log "Rebuilding Next.js bundle..."
  cd "$WEB_DIR"
  # Reinstall only if package.json changed
  echo "$CHANGED" | grep -q 'apps/web/package.json' && pnpm install || true
  pnpm build
  cp -r .next/static .next/standalone/.next/static
  cp -r public .next/standalone/public 2>/dev/null || true
  ok "Next.js bundle rebuilt"
else
  log "No web changes — skipping Next.js rebuild"
fi

# ── 6. Start services ────────────────────────────────────────────────────────

log "Starting API..."
sudo systemctl start bharat-legal-api
log "Waiting for API health..."
for i in $(seq 1 15); do
  response=$(curl -s http://localhost:8000/api/health 2>/dev/null || true)
  echo "$response" | grep -q '"ok"' && { ok "API healthy"; break; } || true
  [ "$i" -eq 15 ] && err "API did not become healthy in time"
  sleep 2
done

log "Starting web..."
sudo systemctl start bharat-legal-web
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002)
[ "$HTTP_CODE" = "200" ] && ok "Web healthy (HTTP $HTTP_CODE)" || err "Web returned HTTP $HTTP_CODE"

# ── 7. Verify ────────────────────────────────────────────────────────────────

log "Tunnel health checks..."
API_TUNNEL=$(curl -s https://rag-api.shubhammathur.in/api/health 2>/dev/null || echo "unreachable")
WEB_TUNNEL=$(curl -s -o /dev/null -w "%{http_code}" https://rag.shubhammathur.in 2>/dev/null || echo "0")

echo "$API_TUNNEL" | grep -q '"ok"' \
  && ok "API tunnel: $API_TUNNEL" \
  || echo "[deploy] ⚠ API tunnel: $API_TUNNEL (may take a moment)"

[ "$WEB_TUNNEL" = "200" ] \
  && ok "Web tunnel: HTTP $WEB_TUNNEL" \
  || echo "[deploy] ⚠ Web tunnel: HTTP $WEB_TUNNEL (may take a moment)"

log "Memory:"
free -h | grep Mem

log "Done."
