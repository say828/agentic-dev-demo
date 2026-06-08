# -*- coding: utf-8 -*-
"""UI parity: 미니홈피 메인 렌더가 스냅샷과 일치 (Playwright exactness 대용)."""
import pathlib

from server.contexts.cyworld import screens

SNAP = (pathlib.Path(__file__).resolve().parents[1]
        / "sdd/04_verify/10_test/ui_parity/minihompy.html")


def test_minihompy_screen_parity():
    want = SNAP.read_text(encoding="utf-8").strip()
    got = screens.render("minihompy").strip()
    assert got == want


def test_minihompy_screen_essentials():
    html = screens.render("minihompy")
    assert "님의 미니홈피" in html
    assert 'class="today"' in html
    assert "방명록" in html
