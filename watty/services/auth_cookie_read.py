"""Leitura de tokens no CookieManager (lógica isolada, testável sem Streamlit).

O ``CookieManager`` de ``extra_streamlit_components`` preenche ``self.cookies`` no
``__init__`` e em ``set``; ``get()`` só lê esse dicionário e **não** volta a pedir
dados ao iframe. Após refresh da página, é obrigatório chamar ``get_all()`` antes
de ``get()`` para sincronizar com o browser.
"""

from __future__ import annotations

from typing import Any, Protocol


class CookieManagerLike(Protocol):
    def get_all(self, key: str = "get_all") -> Any: ...

    def get(self, cookie: str) -> Any: ...


def refresh_and_read_auth_tokens(
    cm: CookieManagerLike,
    *,
    access_key: str,
    refresh_key: str,
    pull_widget_key: str,
) -> tuple[str, str]:
    cm.get_all(key=pull_widget_key)
    at = (cm.get(access_key) or "").strip()
    rt = (cm.get(refresh_key) or "").strip()
    return at, rt
