#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${DASHBOARD_PORT:-8765}"
BASE="http://127.0.0.1:${PORT}"

# Ensure server is up
if ! curl -sf "${BASE}/api/health" >/dev/null 2>&1; then
  echo "[demo] Server not healthy — starting via ${ROOT}/scripts/start.sh"
  bash "${ROOT}/scripts/start.sh"
fi

echo "[demo] Metrics BEFORE:"
curl -sf "${BASE}/api/metrics" | python3 -m json.tool

echo "[demo] Running demo increments (3 ticks)..."
for i in 1 2 3; do
  curl -sf -X POST "${BASE}/api/demo" | python3 -m json.tool
  sleep 0.3
done

echo "[demo] Metrics AFTER:"
AFTER="$(curl -sf "${BASE}/api/metrics")"
echo "${AFTER}" | python3 -m json.tool

python3 - << PY
import json, sys
m = json.loads("""${AFTER}""")
assert m["total_users"] > 0, "total_users must be > 0 after demo"
assert m["active_sessions"] > 0, "active_sessions must be > 0 after demo"
assert m["revenue_ytd"] > 0, "revenue_ytd must be > 0 after demo"
assert m["demo_runs"] >= 3, "demo_runs should reflect demo execution"
print("[demo] VALIDATION PASS — all metrics updated and non-zero")
PY

echo "[demo] Open dashboard: ${BASE}/"
echo "[demo] Semantic page: ${BASE}/index_semantic.html"
