#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"
PORT="${DASHBOARD_PORT:-8080}"
PID_FILE="${ROOT}/.dashboard.pid"
LOG_FILE="${ROOT}/.dashboard.log"

# Avoid duplicate services
if [[ -f "${PID_FILE}" ]]; then
  OLD_PID="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${OLD_PID}" ]] && kill -0 "${OLD_PID}" 2>/dev/null; then
    if curl -sf "http://127.0.0.1:${PORT}/api/health" >/dev/null 2>&1; then
      echo "[start] Dashboard already running (pid=${OLD_PID}) at http://127.0.0.1:${PORT}/"
      exit 0
    fi
    echo "[start] Stale process ${OLD_PID}; stopping"
    kill "${OLD_PID}" 2>/dev/null || true
    sleep 0.5
  fi
  rm -f "${PID_FILE}"
fi

# Also stop any orphan listeners on the port
if command -v lsof >/dev/null 2>&1; then
  ORPHANS="$(lsof -tiTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${ORPHANS}" ]]; then
    echo "[start] Freeing port ${PORT}: ${ORPHANS}"
    # shellcheck disable=SC2086
    kill ${ORPHANS} 2>/dev/null || true
    sleep 0.5
  fi
fi

export DASHBOARD_PORT="${PORT}"
export DASHBOARD_BIND="${DASHBOARD_BIND:-127.0.0.1}"
nohup python3 "${ROOT}/server.py" >"${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"
sleep 0.8

if ! curl -sf "http://127.0.0.1:${PORT}/api/health" >/dev/null; then
  echo "[start] ERROR: server failed to become healthy. Log:" >&2
  tail -n 40 "${LOG_FILE}" >&2 || true
  exit 1
fi

echo "[start] Dashboard running at http://127.0.0.1:${PORT}/"
echo "[start] PID $(cat "${PID_FILE}") · log ${LOG_FILE}"
