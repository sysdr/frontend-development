#!/usr/bin/env bash
# Stop local dashboard processes and reclaim unused Docker resources.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${DASHBOARD_PORT:-3000}"

echo "== cleanup: stopping local dashboard =="
if [[ -x "${ROOT}/scripts/stop.sh" ]] || [[ -f "${ROOT}/scripts/stop.sh" ]]; then
  bash "${ROOT}/scripts/stop.sh" || true
fi

pkill -f "${ROOT}/server.py" 2>/dev/null || true
if command -v lsof >/dev/null 2>&1; then
  ORPHANS="$(lsof -tiTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${ORPHANS}" ]]; then
    # shellcheck disable=SC2086
    kill ${ORPHANS} 2>/dev/null || true
  fi
fi
rm -f "${ROOT}/.dashboard.pid" "${ROOT}/.dashboard.log" "${ROOT}/.server.pid"

echo "== cleanup: removing local caches =="
find "${ROOT}" \( -type d -name node_modules -o -type d -name venv -o -type d -name .venv \
  -o -type d -name .pytest_cache -o -type d -name __pycache__ -o -type d -iname '*istio*' \) \
  -prune -exec rm -rf {} + 2>/dev/null || true
find "${ROOT}" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.istio.yaml' -o -iname '*istio*.yaml' -o -iname '*istio*.yml' \) \
  -delete 2>/dev/null || true

echo "== cleanup: Docker containers / unused resources =="
if ! command -v docker >/dev/null 2>&1; then
  echo "[cleanup] docker not installed — skipping container prune"
  echo "[cleanup] Done"
  exit 0
fi

# Prefer a short timeout so a hung/unreachable daemon does not block cleanup
if ! timeout 8 docker info >/dev/null 2>&1; then
  echo "[cleanup] docker daemon not reachable — skipping container prune"
  echo "[cleanup] Done"
  exit 0
fi

if [[ -f "${ROOT}/docker-compose.yml" ]] || [[ -f "${ROOT}/compose.yml" ]]; then
  (cd "${ROOT}" && docker compose down --remove-orphans 2>/dev/null) || true
fi

ids="$(docker ps -aq 2>/dev/null || true)"
if [[ -n "${ids}" ]]; then
  echo "[cleanup] Stopping containers..."
  # shellcheck disable=SC2086
  docker stop ${ids} 2>/dev/null || true
  echo "[cleanup] Removing containers..."
  # shellcheck disable=SC2086
  docker rm -f ${ids} 2>/dev/null || true
fi

docker container prune -f 2>/dev/null || true
docker image prune -af 2>/dev/null || true
docker network prune -f 2>/dev/null || true
docker volume prune -f 2>/dev/null || true
docker builder prune -af 2>/dev/null || true
docker system prune -af --volumes 2>/dev/null || true

echo "[cleanup] Done"
