#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${DASHBOARD_PORT:-8765}"
BASE="http://127.0.0.1:${PORT}"
cd "${ROOT}"

echo "== verify: health =="
curl -sf "${BASE}/api/health" | python3 -m json.tool

echo "== verify: pages =="
for path in / /index.html /index_semantic.html /index_non_semantic.html /css/styles.css /js/metrics.js; do
  code="$(curl -sf -o /dev/null -w "%{http_code}" "${BASE}${path}")"
  echo "  ${path} -> ${code}"
  [[ "${code}" == "200" ]]
done

echo "== verify: semantic tags present =="
html="$(curl -sf "${BASE}/index_semantic.html")"
echo "${html}" | grep -q "<header>"
echo "${html}" | grep -q "<nav"
echo "${html}" | grep -q "<main>"
echo "${html}" | grep -q "<footer>"
echo "${html}" | grep -q "<article>"
echo "  semantic structure OK"

echo "== verify: metrics non-zero (run demo if needed) =="
metrics="$(curl -sf "${BASE}/api/metrics")"
users="$(echo "${metrics}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["total_users"])')"
if [[ "${users}" -eq 0 ]]; then
  bash "${ROOT}/scripts/demo.sh"
  metrics="$(curl -sf "${BASE}/api/metrics")"
fi
python3 -c '
import json, sys
m = json.loads(sys.argv[1])
for key in ("total_users", "active_sessions", "revenue_ytd"):
    assert m[key] > 0, f"{key} is zero"
print("  metrics OK:", m)
' "${metrics}"

echo "== verify: PASS =="
