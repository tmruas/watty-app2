"""Custom component Streamlit: onboarding React (ver `frontend/`).

Build do frontend (necessário antes de `streamlit run`):
  cd watty_login_wizard/frontend && npm ci && npm run build
"""

from __future__ import annotations

import os

import streamlit.components.v1 as components

_DIR = os.path.dirname(os.path.abspath(__file__))
_BUILD = os.path.join(_DIR, "frontend", "build")

watty_login_wizard = components.declare_component(
    "watty_login_wizard",
    path=_BUILD,
)


def render_login_wizard(
    *,
    supabase_url: str,
    supabase_anon_key: str,
    supabase_email_redirect_url: str | None = None,
    key: str | None = None,
) -> dict | list | str | int | float | bool | None:
    """Renderiza o wizard; devolve o valor enviado pelo React ou None."""
    kwargs: dict = {
        "supabase_url": supabase_url,
        "supabase_anon_key": supabase_anon_key,
        "key": key,
    }
    if supabase_email_redirect_url and str(supabase_email_redirect_url).strip():
        kwargs["supabase_email_redirect_url"] = str(supabase_email_redirect_url).strip()
    return watty_login_wizard(**kwargs)
