"""Integration tests against a live (or freshly started) dashboard server."""
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = os.environ.get("DASHBOARD_PORT", "3000")
BASE = f"http://127.0.0.1:{PORT}"


def _get(path: str):
    with urllib.request.urlopen(BASE + path, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def _post(path: str):
    req = urllib.request.Request(BASE + path, method="POST", data=b"")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def _ensure_server():
    try:
        _get("/api/health")
        return
    except Exception:
        subprocess.run(["bash", str(ROOT / "scripts" / "start.sh")], check=True, cwd=ROOT)
        time.sleep(0.5)
        _get("/api/health")


def test_health_and_metrics_update():
    _ensure_server()
    status, health = _get("/api/health")
    assert status == 200
    assert health["status"] == "healthy"
    assert health["service"] == "day3-dashboard"

    _post("/api/reset")
    _, before = _get("/api/metrics")
    assert before["cpu_percent"] == 0

    for _ in range(3):
        _post("/api/demo")

    _, after = _get("/api/metrics")
    assert after["cpu_percent"] > 0
    assert after["memory_percent"] > 0
    assert after["disk_percent"] > 0
    assert after["network_mbps"] > 0
    assert after["demo_runs"] >= 3


def test_per_metric_endpoints():
    _ensure_server()
    _post("/api/demo")
    _, cpu = _get("/api/metrics/cpu")
    _, memory = _get("/api/metrics/memory")
    _, disk = _get("/api/metrics/disk")
    _, network = _get("/api/metrics/network")
    assert cpu["cpu_percent"] > 0
    assert memory["memory_percent"] > 0
    assert disk["disk_percent"] > 0
    assert network["network_mbps"] > 0
