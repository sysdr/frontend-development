"""Verify broken vs fixed CSS layout assets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fixed_layout_uses_flex_and_grid():
    css = (ROOT / "css" / "layout-fixed.css").read_text(encoding="utf-8")
    assert "display: flex" in css
    assert "display: grid" in css
    assert "float: none" in css or "float:none" in css.replace(" ", "")


def test_broken_layout_uses_floats():
    css = (ROOT / "css" / "layout-broken.css").read_text(encoding="utf-8")
    assert "float: left" in css


def test_fixed_html_links_fixed_css():
    html = (ROOT / "index_fixed_layout.html").read_text(encoding="utf-8")
    assert "layout-fixed.css" in html
    assert 'data-layout="fixed"' in html
    for mid in ("metric-cpu", "metric-memory", "metric-disk", "metric-network"):
        assert mid in html


def test_broken_html_links_broken_css():
    html = (ROOT / "index_broken_layout.html").read_text(encoding="utf-8")
    assert "layout-broken.css" in html
    assert 'data-layout="broken"' in html


def test_index_is_fixed_layout_copy():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "layout-fixed.css" in index
    assert "System Metrics Dashboard" in index
    assert "<header" in index
    assert "<main" in index
