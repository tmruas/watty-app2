"""Testes para o markup e layout da grelha Watty TV.

Testes de viewport (Playwright), após ``pip install -r requirements-dev.txt`` e
``playwright install chromium``::

    pytest -m playwright tests/test_watty_tv.py
"""

from __future__ import annotations

import pytest

from watty.views.watty_tv import build_watty_tv_grid_html


def _sample_resolved() -> list[tuple[str | None, str | None, str]]:
    return [
        ("https://example.com/a.mp4", "https://example.com/p1.png", "Título A"),
        ("https://example.com/b.mp4", "https://example.com/p2.png", "Título B"),
    ]


@pytest.fixture
def sample_html() -> str:
    return build_watty_tv_grid_html(_sample_resolved())


def test_markup_excludes_removed_social_elements(sample_html: str) -> None:
    for fragment in (
        'class="likes"',
        "class='likes'",
        "class=\"who\"",
        "class=\"when\"",
        "avatar-ph",
        '<div class="row"',
        'class="top"',
        'class="shade"',
        "Equipa Watty",
        "2026-4-14",
        "10.1K",
        ">212<",
    ):
        assert fragment not in sample_html


def test_markup_includes_video_title_and_grid(sample_html: str) -> None:
    assert "watty-tv-grid" in sample_html
    assert "gap: 1.5rem" in sample_html
    assert "<video" in sample_html
    assert "controls playsinline" in sample_html
    assert "Título A" in sample_html
    assert "Título B" in sample_html
    assert "card-title" in sample_html


def test_responsive_grid_css(sample_html: str) -> None:
    assert "grid-template-columns: 1fr" in sample_html
    assert "min-width: 768px" in sample_html
    assert "repeat(2, minmax(0, 1fr))" in sample_html
    assert "min-width: 1100px" in sample_html
    assert "repeat(auto-fit, minmax(260px, 1fr))" in sample_html


@pytest.mark.playwright
def test_viewport_mobile_stacks_cards_vertically(sample_html: str) -> None:
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as exc:  # noqa: BLE001 — ambiente sem browser
            pytest.skip(f"Playwright Chromium indisponível: {exc}")
        try:
            page = browser.new_page(viewport={"width": 375, "height": 800})
            page.set_content(sample_html)
            cards = page.locator(".card")
            assert cards.count() == 2
            b0 = cards.nth(0).bounding_box()
            b1 = cards.nth(1).bounding_box()
            assert b0 is not None and b1 is not None
            assert b1["y"] > b0["y"] + b0["height"] * 0.5
        finally:
            browser.close()


@pytest.mark.playwright
def test_viewport_desktop_places_cards_side_by_side(sample_html: str) -> None:
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"Playwright Chromium indisponível: {exc}")
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.set_content(sample_html)
            cards = page.locator(".card")
            assert cards.count() == 2
            b0 = cards.nth(0).bounding_box()
            b1 = cards.nth(1).bounding_box()
            assert b0 is not None and b1 is not None
            assert b1["x"] > b0["x"] + b0["width"] * 0.5
        finally:
            browser.close()
