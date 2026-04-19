"""Garante que a leitura de tokens força sync com o browser (regressão cache stale)."""

from __future__ import annotations

import pytest

from watty.services.auth_cookie_read import refresh_and_read_auth_tokens


class StaleThenLiveCookieManager:
    """Mimetiza extra_streamlit_components.CookieManager: get() usa cache sem get_all."""

    def __init__(self) -> None:
        self._jar: dict[str, str] = {}
        self.get_all_calls: list[str] = []

    def get_all(self, key: str = "get_all") -> dict[str, str]:
        self.get_all_calls.append(key)
        self._jar = {
            "watty_supabase_at": "access-token-xyz",
            "watty_supabase_rt": "refresh-token-abc",
        }
        return self._jar

    def get(self, cookie: str) -> str | None:
        return self._jar.get(cookie)


def test_refresh_and_read_calls_get_all_before_returning_tokens() -> None:
    cm = StaleThenLiveCookieManager()
    cm._jar = {}
    at, rt = refresh_and_read_auth_tokens(
        cm,
        access_key="watty_supabase_at",
        refresh_key="watty_supabase_rt",
        pull_widget_key="watty_auth_pull_browser_cookies",
    )
    assert cm.get_all_calls == ["watty_auth_pull_browser_cookies"]
    assert at == "access-token-xyz"
    assert rt == "refresh-token-abc"


def test_empty_after_get_all_returns_empty_strings() -> None:
    class EmptyCM:
        def __init__(self) -> None:
            self._jar: dict[str, str] = {}

        def get_all(self, key: str = "get_all") -> dict[str, str]:
            self._jar = {}
            return {}

        def get(self, cookie: str) -> str | None:
            return self._jar.get(cookie)

    at, rt = refresh_and_read_auth_tokens(
        EmptyCM(),
        access_key="watty_supabase_at",
        refresh_key="watty_supabase_rt",
        pull_widget_key="pull",
    )
    assert at == ""
    assert rt == ""


@pytest.mark.parametrize(
    "raw_at,raw_rt,expected_at,expected_rt",
    [
        ("  tok  ", "  ref  ", "tok", "ref"),
        ("", "ref", "", "ref"),
        ("tok", "", "tok", ""),
    ],
)
def test_strips_whitespace(
    raw_at: str, raw_rt: str, expected_at: str, expected_rt: str
) -> None:
    class CM:
        def get_all(self, key: str = "get_all") -> None:
            self._jar = {"watty_supabase_at": raw_at, "watty_supabase_rt": raw_rt}

        def get(self, cookie: str) -> str:
            return str(self._jar.get(cookie, "") or "")

    cm = CM()
    at, rt = refresh_and_read_auth_tokens(
        cm,
        access_key="watty_supabase_at",
        refresh_key="watty_supabase_rt",
        pull_widget_key="p",
    )
    assert at == expected_at
    assert rt == expected_rt
