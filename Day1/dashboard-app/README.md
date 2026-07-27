# Semantic HTML Dashboard

Self-contained Day 1 dashboard: compare non-semantic vs semantic HTML and drive live metrics through a demo API.

## Requirements

- Python 3.10+
- Optional: `pytest` for tests (see `requirements.txt`)

```bash
python3 -m pip install -r requirements.txt
```

## Quick start

From this directory:

```bash
bash scripts/start.sh
bash scripts/demo.sh
bash scripts/verify.sh
python3 -m pytest tests -q
bash scripts/stop.sh
```

Cleanup local processes, caches, and unused Docker resources:

```bash
bash cleanup.sh
```

## URLs (default port 8765)

| Page | URL |
|------|-----|
| Dashboard (semantic) | http://127.0.0.1:8765/ |
| Semantic HTML | http://127.0.0.1:8765/index_semantic.html |
| Non-semantic HTML | http://127.0.0.1:8765/index_non_semantic.html |
| Metrics API | http://127.0.0.1:8765/api/metrics |
| Health | http://127.0.0.1:8765/api/health |

Override the port with `DASHBOARD_PORT` if needed.

## Layout

```
.
├── index.html                 # Main entry (semantic)
├── index_semantic.html
├── index_non_semantic.html
├── css/styles.css
├── js/metrics.js
├── js/demo.js
├── server.py                  # Stdlib HTTP server + metrics API
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
- Runtime depends only on files in this directory (`scripts/start.sh` → `server.py`).
