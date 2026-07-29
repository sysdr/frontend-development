#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${DASHBOARD_PORT:-8080}"
BASE="http://127.0.0.1:${PORT}"
cd "${ROOT}"

echo "== verify: health =="
curl -sf "${BASE}/api/health" | python3 -m json.tool

echo "== verify: pages =="
for path in / /index.html /index_fixed_layout.html /index_broken_layout.html /css/styles.css /css/layout-fixed.css /css/layout-broken.css /js/metrics.js; do
  code="$(curl -sf -o /dev/null -w "%{http_code}" "${BASE}${path}")"
  echo "  ${path} -> ${code}"
  [[ "${code}" == "200" ]]
done

echo "== verify: fixed layout uses grid =="
css="$(curl -sf "${BASE}/css/layout-fixed.css")"
echo "${css}" | grep -q "display: grid"
echo "${css}" | grep -q "display: flex"
echo "  flex + grid OK"

echo "== verify: broken layout uses floats =="
broken="$(curl -sf "${BASE}/css/layout-broken.css")"
echo "${broken}" | grep -q "float: left"
echo "  float failure demo OK"

echo "== verify: metrics non-zero (run demo if needed) =="
metrics="$(curl -sf "${BASE}/api/metrics")"
cpu="$(echo "${metrics}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["cpu_percent"])')"
# bash float compare via python
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
