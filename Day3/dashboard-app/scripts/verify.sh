#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${DASHBOARD_PORT:-3000}"
BASE="http://127.0.0.1:${PORT}"
cd "${ROOT}"

echo "== verify: health =="
curl -sf "${BASE}/api/health" | python3 -m json.tool

echo "== verify: pages =="
for path in / /index.html /index_parallel.html /index_sequential.html /css/styles.css /css/waterfall.css /js/metrics.js /js/waterfall.js /js/demo.js; do
  code="$(curl -sf -o /dev/null -w "%{http_code}" "${BASE}${path}")"
  echo "  ${path} -> ${code}"
  [[ "${code}" == "200" ]]
done

echo "== verify: per-metric endpoints =="
for ep in cpu memory disk network; do
  code="$(curl -sf -o /dev/null -w "%{http_code}" "${BASE}/api/metrics/${ep}")"
  echo "  /api/metrics/${ep} -> ${code}"
  [[ "${code}" == "200" ]]
done

echo "== verify: waterfall JS present =="
js="$(curl -sf "${BASE}/js/waterfall.js")"
echo "${js}" | grep -q "renderNetworkWaterfall"
echo "  waterfall renderer OK"

echo "== verify: metrics.js has sequential + parallel =="
mjs="$(curl -sf "${BASE}/js/metrics.js")"
echo "${mjs}" | grep -q "refreshSequential"
echo "${mjs}" | grep -q "Promise.all"
echo "  fetch modes OK"

echo "== verify: metrics non-zero (run demo if needed) =="
metrics="$(curl -sf "${BASE}/api/metrics")"
cpu="$(echo "${metrics}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["cpu_percent"])')"
need_demo="$(python3 -c "print(1 if float('${cpu}') == 0 else 0)")"
if [[ "${need_demo}" -eq 1 ]]; then
  bash "${ROOT}/scripts/demo.sh"
  metrics="$(curl -sf "${BASE}/api/metrics")"
fi
python3 -c '
import json, sys
m = json.loads(sys.argv[1])
for key in ("cpu_percent", "memory_percent", "disk_percent", "network_mbps"):
    assert float(m[key]) > 0, f"{key} is zero"
print("  metrics OK:", m)
' "${metrics}"

echo "== verify: PASS =="
