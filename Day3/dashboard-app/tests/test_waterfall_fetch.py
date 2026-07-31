"""Client JS encodes sequential vs parallel fetch + waterfall renderer."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_metrics_js_has_fetch_modes():
    text = (ROOT / "js" / "metrics.js").read_text(encoding="utf-8")
    assert "/api/metrics/cpu" in text
    assert "/api/metrics/memory" in text
    assert "/api/metrics/disk" in text
    assert "/api/metrics/network" in text
    assert "refreshSequential" in text
    assert "Promise.all" in text
    assert "performance.now" in text


def test_waterfall_js_renderer():
    text = (ROOT / "js" / "waterfall.js").read_text(encoding="utf-8")
    assert "renderNetworkWaterfall" in text
    assert "waterfall-bar" in text


def test_html_pages_wire_waterfall():
    for name in ("index.html", "index_parallel.html", "index_sequential.html"):
        html = (ROOT / name).read_text(encoding="utf-8")
        assert 'id="waterfall"' in html
        assert "js/waterfall.js" in html
        assert "js/metrics.js" in html
        assert 'id="metric-cpu"' in html
        assert 'id="metric-memory"' in html
        assert 'id="metric-disk"' in html
        assert 'id="metric-network"' in html
        assert 'id="btn-refresh"' in html
        assert "Refresh Now" in html

    seq = (ROOT / "index_sequential.html").read_text(encoding="utf-8")
    assert 'data-fetch-mode="sequential"' in seq
    par = (ROOT / "index_parallel.html").read_text(encoding="utf-8")
    assert 'data-fetch-mode="parallel"' in par
