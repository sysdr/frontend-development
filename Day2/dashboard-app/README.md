# System Metrics Dashboard — CSS Layout (Day 2)

Self-contained Day 2 lab: compare a broken float layout vs a fixed Flexbox + CSS Grid layout, with live system metrics driven by a demo API.

This directory is the runnable project. It does **not** depend on the parent `setup.sh` — clone or copy only `dashboard-app/` and use the scripts below.

## Requirements

- Python 3.10+
- Optional: `pytest` for tests (see `requirements.txt`)

```bash
python3 -m pip install -r requirements.txt
```

## Quick start

From this directory (`dashboard-app/`):

```bash
bash scripts/start.sh
bash scripts/demo.sh
bash scripts/verify.sh
python3 -m pytest tests -q
bash scripts/stop.sh
```

Cleanup local processes, caches (`node_modules`, `venv`, `.pytest_cache`, `__pycache__`, `*.pyc`, Istio artifacts), and unused Docker resources:

```bash
bash cleanup.sh
```

## URLs (default port 8080)

| Page | URL |
|------|-----|
| Dashboard (fixed layout) | http://127.0.0.1:8080/ |
| Fixed layout | http://127.0.0.1:8080/index_fixed_layout.html |
| Broken layout (failure demo) | http://127.0.0.1:8080/index_broken_layout.html |
| Metrics API | http://127.0.0.1:8080/api/metrics |
| Health | http://127.0.0.1:8080/api/health |

Override the port with `DASHBOARD_PORT` if needed.

## Layout

```
.
├── index.html                 # Main entry (fixed layout)
├── index_fixed_layout.html
├── index_broken_layout.html
├── css/styles.css
├── css/layout-fixed.css
├── css/layout-broken.css
├── js/metrics.js
├── js/demo.js
├── js/layout-demo.js
├── server.py
├── metrics.json
├── requirements.txt
├── cleanup.sh
├── scripts/
│   ├── start.sh
│   ├── stop.sh
│   ├── demo.sh
│   └── verify.sh
└── tests/
```

## Notes

- No API keys or external credentials are required.
- Runtime depends only on files in this directory (`scripts/start.sh` → `server.py`). Parent `setup.sh` is optional scaffolding only.
- Runbook: open the broken layout to see float overflow, then switch to fixed layout; run `scripts/demo.sh` so metric cards show non-zero values.
