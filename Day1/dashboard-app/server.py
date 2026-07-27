#!/usr/bin/env python3
"""Day 1 dashboard HTTP server: static files + live metrics API."""
from __future__ import annotations

import json
import os
import random
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
METRICS_PATH = ROOT / "metrics.json"
LOCK = threading.Lock()
PORT = int(os.environ.get("DASHBOARD_PORT", "8765"))
HOST = os.environ.get("DASHBOARD_BIND", "127.0.0.1")


def read_metrics() -> dict:
    with LOCK:
        if not METRICS_PATH.exists():
            return {
                "total_users": 0,
                "active_sessions": 0,
                "revenue_ytd": 0,
                "demo_runs": 0,
                "updated_at": None,
            }
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def write_metrics(data: dict) -> None:
    with LOCK:
        METRICS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def bump_demo_metrics() -> dict:
    data = read_metrics()
    data["total_users"] = int(data.get("total_users") or 0) + random.randint(1200, 4800)
    data["active_sessions"] = max(
        1, int(data.get("active_sessions") or 0) + random.randint(80, 420)
    )
    data["revenue_ytd"] = int(data.get("revenue_ytd") or 0) + random.randint(25_000, 95_000)
    data["demo_runs"] = int(data.get("demo_runs") or 0) + 1
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_metrics(data)
    return data


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        # Quieter logs; still show API hits
        if args and isinstance(args[0], str) and "/api/" in args[0]:
            super().log_message(fmt, *args)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/metrics":
            self._send_json(read_metrics())
            return
        if path == "/api/health":
            self._send_json({"status": "healthy", "service": "day1-dashboard"})
            return
        if path in ("/", "/index.html"):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/demo":
            self._send_json({"ok": True, "metrics": bump_demo_metrics()})
            return
        if path == "/api/reset":
            write_metrics(
                {
                    "total_users": 0,
                    "active_sessions": 0,
                    "revenue_ytd": 0,
                    "demo_runs": 0,
                    "updated_at": None,
                }
            )
            self._send_json({"ok": True, "metrics": read_metrics()})
            return
        self._send_json({"error": "not found"}, 404)


def main() -> None:
    # Ensure metrics file exists
    if not METRICS_PATH.exists():
        write_metrics(
            {
                "total_users": 0,
                "active_sessions": 0,
                "revenue_ytd": 0,
                "demo_runs": 0,
                "updated_at": None,
            }
        )
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"[server] Day1 dashboard at http://{HOST}:{PORT}/")
    print(f"[server] Semantic: http://{HOST}:{PORT}/index_semantic.html")
    print(f"[server] Metrics API: http://{HOST}:{PORT}/api/metrics")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
