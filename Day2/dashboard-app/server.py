#!/usr/bin/env python3
"""Day 2 dashboard HTTP server: static files + live system-metrics API."""
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
PORT = int(os.environ.get("DASHBOARD_PORT", "8080"))
HOST = os.environ.get("DASHBOARD_BIND", "127.0.0.1")


def default_metrics() -> dict:
    return {
        "cpu_percent": 0,
        "memory_percent": 0,
        "disk_percent": 0,
        "network_mbps": 0,
        "demo_runs": 0,
        "updated_at": None,
    }


def read_metrics() -> dict:
    with LOCK:
        if not METRICS_PATH.exists():
            return default_metrics()
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def write_metrics(data: dict) -> None:
    with LOCK:
        METRICS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def bump_demo_metrics() -> dict:
    data = read_metrics()
    # Simulate realistic non-zero host metrics after each demo tick
    data["cpu_percent"] = round(min(99.0, max(5.0, float(data.get("cpu_percent") or 0) + random.uniform(8, 22))), 1)
    data["memory_percent"] = round(min(98.0, max(10.0, float(data.get("memory_percent") or 0) + random.uniform(6, 18))), 1)
    data["disk_percent"] = round(min(95.0, max(12.0, float(data.get("disk_percent") or 0) + random.uniform(3, 12))), 1)
    data["network_mbps"] = round(max(1.0, float(data.get("network_mbps") or 0) + random.uniform(15, 85)), 1)
    data["demo_runs"] = int(data.get("demo_runs") or 0) + 1
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_metrics(data)
    return data


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
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
            self._send_json({"status": "healthy", "service": "day2-dashboard"})
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
            write_metrics(default_metrics())
            self._send_json({"ok": True, "metrics": read_metrics()})
            return
        self._send_json({"error": "not found"}, 404)


def main() -> None:
    if not METRICS_PATH.exists():
        write_metrics(default_metrics())
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"[server] Day2 dashboard at http://{HOST}:{PORT}/")
    print(f"[server] Fixed layout: http://{HOST}:{PORT}/index_fixed_layout.html")
    print(f"[server] Broken layout: http://{HOST}:{PORT}/index_broken_layout.html")
    print(f"[server] Metrics API: http://{HOST}:{PORT}/api/metrics")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
