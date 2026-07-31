#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${DASHBOARD_PORT:-3000}"
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
assert m["cpu_percent"] > 0, "cpu_percent must be > 0 after demo"
assert m["memory_percent"] > 0, "memory_percent must be > 0 after demo"
assert m["disk_percent"] > 0, "disk_percent must be > 0 after demo"
assert m["network_mbps"] > 0, "network_mbps must be > 0 after demo"
assert m["demo_runs"] >= 3, "demo_runs should reflect demo execution"
print("[demo] VALIDATION PASS — all metrics updated and non-zero")
PY

echo "[demo] Per-metric endpoints:"
for ep in cpu memory disk network; do
  echo "  /api/metrics/${ep}:"
  curl -sf "${BASE}/api/metrics/${ep}" | python3 -m json.tool
done

echo "[demo] Open dashboard: ${BASE}/"
echo "[demo] Parallel: ${BASE}/index_parallel.html"
echo "[demo] Sequential: ${BASE}/index_sequential.html"
