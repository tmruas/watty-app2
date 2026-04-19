"""Testes para leitura de dimensões JPEG (sidebar)."""

import pytest

from watty.paths import read_jpeg_dimensions, read_raster_dimensions, watty_logosuperior_path, watty_sidebar_width_px


def test_read_raster_dimensions_on_logo_when_present() -> None:
    p = watty_logosuperior_path()
    if not p.is_file():
        pytest.skip("logo watty_logosuperior.* ausente")
    dims = read_raster_dimensions(p)
    assert dims is not None
    w, h = dims
    assert w > 0 and h > 0
    if p.suffix.lower() in (".jpg", ".jpeg"):
        assert read_jpeg_dimensions(p) == dims


def test_watty_sidebar_width_px_clamped() -> None:
    p = watty_logosuperior_path()
    if not p.is_file():
        pytest.skip("logo watty_logosuperior.* ausente")
    n = watty_sidebar_width_px(p)
    assert 200 <= n <= 520
