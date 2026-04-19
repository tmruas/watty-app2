"""Validação de sessão Supabase no servidor (Streamlit)."""

from __future__ import annotations

from supabase import Client, create_client
from supabase_auth.errors import AuthApiError


def create_service_client(supabase_url: str, service_role_key: str) -> Client:
    return create_client(supabase_url, service_role_key)


def get_user_email_and_metadata(
    access_token: str, *, supabase_url: str, service_role_key: str
) -> tuple[str, dict]:
    """Verifica o JWT de acesso e devolve (email_normalizado, user_metadata)."""
    client = create_service_client(supabase_url, service_role_key)
    try:
        res = client.auth.get_user(access_token)
    except AuthApiError as e:
        raise ValueError(e.message) from e
    if res is None or res.user is None:
        raise ValueError("Sessão inválida ou expirada.")
    email = (res.user.email or "").strip().lower()
    if not email:
        raise ValueError("A conta não tem email associado.")
    meta = dict(res.user.user_metadata or {})
    return email, meta
