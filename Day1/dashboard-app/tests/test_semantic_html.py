"""Verify semantic vs non-semantic HTML structure."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_semantic_file_has_landmarks():
    html = (ROOT / "index_semantic.html").read_text(encoding="utf-8")
    for tag in ("<header>", "<nav", "<main>", "<section", "<article>", "<footer>"):
        assert tag in html, f"missing semantic tag: {tag}"
    assert "<div class=\"header\">" not in html


def test_non_semantic_uses_divs():
    html = (ROOT / "index_non_semantic.html").read_text(encoding="utf-8")
    assert '<div class="header">' in html
    assert "<header>" not in html
    assert "<main>" not in html


def test_index_is_semantic_copy():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    semantic = (ROOT / "index_semantic.html").read_text(encoding="utf-8")
    assert "<header>" in index
    assert "<main>" in index
    assert "data-metric=" in index or "metric-users" in index
    # index should match semantic content closely
    assert "Dashboard Overview" in index
    assert "Dashboard Overview" in semantic
