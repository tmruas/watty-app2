"""Persistência de sessão Supabase (cookies) e encerramento de sessão."""

from __future__ import annotations

import datetime
import streamlit as st
from extra_streamlit_components import CookieManager
from supabase import create_client

from watty.services.auth_cookie_read import refresh_and_read_auth_tokens
from watty.services.sheets import carregar_perfil
from watty.services.supabase_auth import get_user_email_and_metadata

# Chave do widget Streamlit (única por sessão — ver get_cookie_manager).
COOKIE_MANAGER_COMPONENT_KEY = "watty_auth_cookie_manager"
_SESSION_STATE_COOKIE_MANAGER = "_watty_cookie_manager_singleton"
# O CookieManager só recebe os cookies do browser após o iframe montar;
# na 1.ª execução após refresh `get()` vem vazio — um rerun evita logout falso.
_COOKIE_JS_SYNCED = "_watty_cookie_js_synced"
COOKIE_ACCESS = "watty_supabase_at"
COOKIE_REFRESH = "watty_supabase_rt"
# Cookie de refresh no Supabase: ordem de grandeza de dias; margem confortável.
COOKIE_MAX_AGE_DAYS = 14
# Após logout explícito: não voltar a reconstruir sessão a partir de cookies nesta sessão Streamlit
# (evita re-login imediato se o iframe ainda não reflectiu o delete).
_SKIP_RESTORE_UNTIL_LOGIN = "_watty_skip_restore_until_login"


def _max_age_seconds() -> float:
    return float(COOKIE_MAX_AGE_DAYS * 24 * 3600)


def _expires_at() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=COOKIE_MAX_AGE_DAYS)


def get_cookie_manager() -> CookieManager:
    """Uma instância por sessão Streamlit: evita StreamlitDuplicateElementKey no mesmo run."""
    if _SESSION_STATE_COOKIE_MANAGER not in st.session_state:
        st.session_state[_SESSION_STATE_COOKIE_MANAGER] = CookieManager(
            key=COOKIE_MANAGER_COMPONENT_KEY
        )
    return st.session_state[_SESSION_STATE_COOKIE_MANAGER]


def save_auth_tokens_to_cookies(access_token: str, refresh_token: str) -> None:
    """Grava tokens no browser (persistência após refresh da página)."""
    at = (access_token or "").strip()
    rt = (refresh_token or "").strip()
    if not at or not rt:
        return
    cm = get_cookie_manager()
    opts = dict(
        path="/",
        expires_at=_expires_at(),
        max_age=_max_age_seconds(),
        same_site="lax",
    )
    cm.set(COOKIE_ACCESS, at, key="watty_cookie_set_at", **opts)
    cm.set(COOKIE_REFRESH, rt, key="watty_cookie_set_rt", **opts)


def clear_auth_cookies() -> None:
    cm = get_cookie_manager()
    for key, dk in ((COOKIE_ACCESS, "watty_cookie_del_at"), (COOKIE_REFRESH, "watty_cookie_del_rt")):
        try:
            cm.delete(key, key=dk)
        except Exception:
            pass


def _read_tokens_from_cookies() -> tuple[str, str]:
    cm = get_cookie_manager()
    return refresh_and_read_auth_tokens(
        cm,
        access_key=COOKIE_ACCESS,
        refresh_key=COOKIE_REFRESH,
        pull_widget_key="watty_auth_pull_browser_cookies",
    )


def try_restore_session_from_cookies() -> bool:
    """
    Se existirem cookies válidos, reconstrói st.session_state como após login.
    Devolve True se o utilizador ficou autenticado.
    """
    if st.session_state.get("logado"):
        return True
    if st.session_state.get(_SKIP_RESTORE_UNTIL_LOGIN):
        return False
    try:
        supabase_url = str(st.secrets["SUPABASE_URL"]).strip()
        supabase_anon = str(st.secrets["SUPABASE_ANON_KEY"]).strip()
        service_role = str(st.secrets["SUPABASE_SERVICE_ROLE_KEY"]).strip()
    except Exception:
        return False

    get_cookie_manager()
    if not st.session_state.get(_COOKIE_JS_SYNCED):
        st.session_state[_COOKIE_JS_SYNCED] = True
        st.rerun()

    access_token, refresh_token = _read_tokens_from_cookies()
    if not access_token or not refresh_token:
        return False

    client = create_client(supabase_url, supabase_anon)
    try:
        auth_resp = client.auth.set_session(access_token, refresh_token)
    except Exception:
        clear_auth_cookies()
        return False

    sess = getattr(auth_resp, "session", None)
    if sess is None:
        clear_auth_cookies()
        return False
    new_at = (getattr(sess, "access_token", None) or "").strip()
    new_rt = (getattr(sess, "refresh_token", None) or "").strip()
    if not new_at:
        clear_auth_cookies()
        return False

    try:
        email, meta, created_at = get_user_email_and_metadata(
            new_at,
            supabase_url=supabase_url,
            service_role_key=service_role,
        )
    except Exception:
        clear_auth_cookies()
        return False

    nome_display = str(meta.get("nome_display") or meta.get("nome") or "").strip()
    if not nome_display:
        nome_display = email.split("@", 1)[0]
    nome_aluno = email

    try:
        xp_bd, nivel_bd, streak_bd, linha_bd = carregar_perfil(nome_aluno)
    except Exception:
        clear_auth_cookies()
        return False

    st.session_state.logado = True
    st.session_state["nome_aluno"] = nome_aluno
    st.session_state["nome_display"] = nome_display
    st.session_state.xp = xp_bd
    st.session_state.nivel = nivel_bd
    st.session_state.streak = streak_bd
    st.session_state.linha_bd = linha_bd
    st.session_state["user_created_at"] = created_at

    if new_rt:
        save_auth_tokens_to_cookies(new_at, new_rt)
    st.session_state.pop(_SKIP_RESTORE_UNTIL_LOGIN, None)
    return True


def logout_clear_session() -> None:
    """Termina sessão local, revoga sessão Supabase quando possível e apaga cookies de auth."""
    try:
        supabase_url = str(st.secrets["SUPABASE_URL"]).strip()
        supabase_anon = str(st.secrets["SUPABASE_ANON_KEY"]).strip()
    except Exception:
        supabase_url = ""
        supabase_anon = ""

    if supabase_url and supabase_anon:
        try:
            access_token, refresh_token = _read_tokens_from_cookies()
            if access_token:
                client = create_client(supabase_url, supabase_anon)
                try:
                    if refresh_token:
                        client.auth.set_session(access_token, refresh_token)
                    client.auth.sign_out()
                except Exception:
                    pass
        except Exception:
            pass

    clear_auth_cookies()
    st.session_state.pop(_COOKIE_JS_SYNCED, None)
    st.session_state.pop(_SESSION_STATE_COOKIE_MANAGER, None)
    for k in (
        "nome_aluno",
        "nome_display",
        "xp",
        "nivel",
        "streak",
        "linha_bd",
        "user_created_at",
    ):
        st.session_state.pop(k, None)
    st.session_state.logado = False
    st.session_state.ui_route = "main"
    st.session_state[_SKIP_RESTORE_UNTIL_LOGIN] = True
    st.rerun()


def clear_skip_restore_after_login() -> None:
    """Chamar após login bem-sucedido para voltar a permitir restaurar sessão a partir de cookies."""
    st.session_state.pop(_SKIP_RESTORE_UNTIL_LOGIN, None)
