#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${DASHBOARD_PORT:-8080}"
PID_FILE="${ROOT}/.dashboard.pid"

if [[ -f "${PID_FILE}" ]]; then
  PID="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${PID}" ]] && kill -0 "${PID}" 2>/dev/null; then
    echo "[stop] Stopping dashboard pid=${PID}"
    kill "${PID}" 2>/dev/null || true
    sleep 0.4
    kill -9 "${PID}" 2>/dev/null || true
  fi
  rm -f "${PID_FILE}"
fi

if command -v lsof >/dev/null 2>&1; then
  ORPHANS="$(lsof -tiTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${ORPHANS}" ]]; then
    echo "[stop] Killing listeners on ${PORT}: ${ORPHANS}"
    # shellcheck disable=SC2086
    kill ${ORPHANS} 2>/dev/null || true
  fi
fi

echo "[stop] Done"
