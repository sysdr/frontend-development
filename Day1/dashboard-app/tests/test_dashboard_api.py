"""Integration tests against a live (or freshly started) dashboard server."""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = os.environ.get("DASHBOARD_PORT", "8765")
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

    _post("/api/reset")
    _, before = _get("/api/metrics")
    assert before["total_users"] == 0

    for _ in range(3):
        _post("/api/demo")

    _, after = _get("/api/metrics")
    assert after["total_users"] > 0
    assert after["active_sessions"] > 0
    assert after["revenue_ytd"] > 0
    assert after["demo_runs"] >= 3
