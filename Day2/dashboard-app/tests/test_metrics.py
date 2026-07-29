"""Metrics file and demo bump logic."""
import json
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_server():
    spec = importlib.util.spec_from_file_location("day2_server", ROOT / "server.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_metrics_json_exists():
    path = ROOT / "metrics.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("cpu_percent", "memory_percent", "disk_percent", "network_mbps", "demo_runs"):
        assert key in data


def test_bump_demo_metrics_updates_values(tmp_path, monkeypatch):
    mod = _load_server()
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text(json.dumps(mod.default_metrics()), encoding="utf-8")
    monkeypatch.setattr(mod, "METRICS_PATH", metrics_path)
    before = mod.read_metrics()
    after = mod.bump_demo_metrics()
    assert after["cpu_percent"] > before["cpu_percent"]
    assert after["memory_percent"] > before["memory_percent"]
    assert after["disk_percent"] > before["disk_percent"]
    assert after["network_mbps"] > before["network_mbps"]
    assert after["demo_runs"] == before["demo_runs"] + 1
    assert after["updated_at"]
