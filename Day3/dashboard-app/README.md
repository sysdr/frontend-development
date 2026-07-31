# System Metrics Dashboard — Network Waterfall (Day 3)

Self-contained Day 3 lab: fetch each metric from its own API endpoint and visualize a **network waterfall**. Compare sequential (await each request) vs parallel (`Promise.all`) fetch modes.

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

## URLs (default port 3000)

| Page | URL |
|------|-----|
| Dashboard (parallel fetch) | http://127.0.0.1:3000/ |
| Parallel waterfall | http://127.0.0.1:3000/index_parallel.html |
| Sequential waterfall | http://127.0.0.1:3000/index_sequential.html |
| Aggregated metrics | http://127.0.0.1:3000/api/metrics |
| Per-metric (waterfall) | http://127.0.0.1:3000/api/metrics/cpu (also `/memory`, `/disk`, `/network`) |
| Health | http://127.0.0.1:3000/api/health |

Override the port with `DASHBOARD_PORT` if needed.

## Layout

```
.
├── index.html                 # Main entry (parallel fetch)
├── index_parallel.html
├── index_sequential.html
├── css/styles.css
├── css/waterfall.css
├── js/metrics.js
├── js/waterfall.js
├── js/demo.js
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
- Runbook: open sequential to see stacked waterfall bars, then parallel for overlapping bars; run `scripts/demo.sh` so metric cards show non-zero values.
