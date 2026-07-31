#!/usr/bin/env python3
"""Day 3 dashboard HTTP server: per-metric APIs + artificial latency for waterfall demos."""
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
PORT = int(os.environ.get("DASHBOARD_PORT", "3000"))
HOST = os.environ.get("DASHBOARD_BIND", "127.0.0.1")

# Artificial per-endpoint latency (ms) so sequential vs parallel waterfall is visible
LATENCY_MS = {
    "cpu": (80, 140),
    "memory": (100, 180),
    "disk": (120, 200),
    "network": (90, 160),
}


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
    data["cpu_percent"] = round(min(99.0, max(5.0, float(data.get("cpu_percent") or 0) + random.uniform(8, 22))), 1)
    data["memory_percent"] = round(min(98.0, max(10.0, float(data.get("memory_percent") or 0) + random.uniform(6, 18))), 1)
    data["disk_percent"] = round(min(95.0, max(12.0, float(data.get("disk_percent") or 0) + random.uniform(3, 12))), 1)
    data["network_mbps"] = round(max(1.0, float(data.get("network_mbps") or 0) + random.uniform(15, 85)), 1)
    data["demo_runs"] = int(data.get("demo_runs") or 0) + 1
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_metrics(data)
    return data


def _sleep_for(metric_key: str) -> None:
    lo, hi = LATENCY_MS.get(metric_key, (50, 100))
    time.sleep(random.uniform(lo, hi) / 1000.0)


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
        metrics = read_metrics()

        if path == "/api/metrics":
            self._send_json(metrics)
            return
        if path == "/api/metrics/cpu":
            _sleep_for("cpu")
            self._send_json({
                "cpu_percent": metrics["cpu_percent"],
                "updated_at": metrics.get("updated_at"),
                "demo_runs": metrics.get("demo_runs", 0),
            })
            return
        if path == "/api/metrics/memory":
            _sleep_for("memory")
            self._send_json({
                "memory_percent": metrics["memory_percent"],
                "updated_at": metrics.get("updated_at"),
                "demo_runs": metrics.get("demo_runs", 0),
            })
            return
        if path == "/api/metrics/disk":
            _sleep_for("disk")
            self._send_json({
                "disk_percent": metrics["disk_percent"],
                "updated_at": metrics.get("updated_at"),
                "demo_runs": metrics.get("demo_runs", 0),
            })
            return
        if path == "/api/metrics/network":
            _sleep_for("network")
            self._send_json({
                "network_mbps": metrics["network_mbps"],
                "updated_at": metrics.get("updated_at"),
                "demo_runs": metrics.get("demo_runs", 0),
            })
            return
        if path in ("/api/health", "/health"):
            self._send_json({"status": "healthy", "service": "day3-dashboard"})
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
    print(f"[server] Day3 dashboard at http://{HOST}:{PORT}/")
    print(f"[server] Parallel: http://{HOST}:{PORT}/index_parallel.html")
    print(f"[server] Sequential: http://{HOST}:{PORT}/index_sequential.html")
    print(f"[server] Metrics API: http://{HOST}:{PORT}/api/metrics")
    print(f"[server] Per-metric: http://{HOST}:{PORT}/api/metrics/cpu")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
