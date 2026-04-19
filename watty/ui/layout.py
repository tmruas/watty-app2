"""Layout principal: login, HUD, sidebar."""

import html
from urllib.parse import quote

import streamlit as st

from watty.config import (
    FOOTER_EMAIL_AJUDA,
    FOOTER_URL_LINKEDIN,
    LISTA_ANOS,
    disciplinas_para_ano,
    exemplo_para_disciplina,
)
from watty.services.auth_session import logout_clear_session, save_auth_tokens_to_cookies
from watty.services.sheets import carregar_perfil
from watty.services.supabase_auth import get_user_email_and_metadata
from watty_login_wizard import render_login_wizard

ABAS = ["💬 Chat Socrático", "🏋️ Treinar (Quizzes)", "📚 Aprender (Resumos)"]


def init_session_state() -> None:
    if "logado" not in st.session_state:
        st.session_state.logado = False
    if "ui_route" not in st.session_state:
        st.session_state.ui_route = "main"


def sync_footer_nav_from_query_params() -> None:
    """Links do rodapé de login usam ?watty_page= — converte para ui_route e limpa o URL."""
    qp = st.query_params
    if "watty_page" not in qp:
        return
    raw = qp.get("watty_page")
    v = raw[0] if isinstance(raw, (list, tuple)) else raw
    v = str(v or "").strip().lower()
    if v == "quem_somos":
        st.session_state.ui_route = "quem_somos"
    elif v == "termos":
        st.session_state.ui_route = "termos"
    try:
        del st.query_params["watty_page"]
    except Exception:
        pass
    st.rerun()


def render_login_gate() -> None:
    try:
        supabase_url = str(st.secrets["SUPABASE_URL"]).strip()
        supabase_anon = str(st.secrets["SUPABASE_ANON_KEY"]).strip()
        service_role = str(st.secrets["SUPABASE_SERVICE_ROLE_KEY"]).strip()
    except Exception:
        st.error(
            "Configura em `.streamlit/secrets.toml` as chaves **SUPABASE_URL**, "
            "**SUPABASE_ANON_KEY** e **SUPABASE_SERVICE_ROLE_KEY** (ver GUIA_EXECUCAO.md)."
        )
        return

    email_redirect = None
    try:
        raw = st.secrets["SUPABASE_EMAIL_REDIRECT_URL"]
        if raw is not None and str(raw).strip():
            email_redirect = str(raw).strip()
    except (KeyError, TypeError, AttributeError):
        pass

    resultado = render_login_wizard(
        key="watty_login_wizard",
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon,
        supabase_email_redirect_url=email_redirect,
    )
    if not resultado or not isinstance(resultado, dict):
        return

    token = str(resultado.get("access_token", "")).strip()
    if not token:
        return

    try:
        email, meta = get_user_email_and_metadata(
            token,
            supabase_url=supabase_url,
            service_role_key=service_role,
        )
    except Exception as e:
        st.error(f"Não foi possível validar a sessão: {e}")
        return

    nome_display = str(resultado.get("nome_display", "")).strip()
    if not nome_display:
        nome_display = str(meta.get("nome_display") or meta.get("nome") or "").strip()
    if not nome_display:
        nome_display = email.split("@", 1)[0]

    nome_aluno = email

    with st.spinner("A carregar o teu progresso na cloud... ☁️"):
        xp_bd, nivel_bd, streak_bd, linha_bd = carregar_perfil(nome_aluno)

        st.session_state.logado = True
        st.session_state["nome_aluno"] = nome_aluno
        st.session_state["nome_display"] = nome_display
        st.session_state.xp = xp_bd
        st.session_state.nivel = nivel_bd
        st.session_state.streak = streak_bd
        st.session_state.linha_bd = linha_bd
    rt = str(resultado.get("refresh_token", "") or "").strip()
    if rt:
        save_auth_tokens_to_cookies(token, rt)
    st.rerun()


def _inject_user_menu_header_css() -> None:
    """Coloca o menu do utilizador na zona do header (junto ao toolbar nativo), responsivo."""
    st.markdown(
        """
<style>
/* Menu utilizador: fixo na zona superior (alinhado ao header Streamlit / Deploy) */
div.element-container.st-key-watty_user_menu_popover {
    position: fixed !important;
    top: max(0.5rem, env(safe-area-inset-top, 0px)) !important;
    right: clamp(3.75rem, 12vw, 6.5rem) !important;
    z-index: 1000020 !important;
    width: auto !important;
    max-width: min(42vw, 16rem) !important;
    margin: 0 !important;
    padding: 0 !important;
}
div.element-container.st-key-watty_user_menu_popover > div {
    width: 100% !important;
}
div.element-container.st-key-watty_user_menu_popover button[kind="secondary"] {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 100% !important;
    font-size: 0.9rem !important;
    min-height: 2.25rem !important;
    padding: 0.35rem 0.55rem !important;
}
@media (max-width: 768px) {
    div.element-container.st-key-watty_user_menu_popover {
        right: clamp(3rem, 18vw, 4.75rem) !important;
        max-width: min(52vw, 13rem) !important;
    }
    div.element-container.st-key-watty_user_menu_popover button[kind="secondary"] {
        font-size: 0.78rem !important;
        padding: 0.28rem 0.4rem !important;
    }
}
@media (max-width: 480px) {
    div.element-container.st-key-watty_user_menu_popover {
        right: clamp(2.5rem, 20vw, 3.75rem) !important;
        max-width: min(58vw, 11rem) !important;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def _truncate_display_name(name: str, max_len: int = 22) -> str:
    n = (name or "").strip()
    if len(n) <= max_len:
        return n or "Conta"
    return n[: max_len - 1] + "…"


def render_app_top_bar() -> None:
    """Voltar (em rotas auxiliares) + menu do utilizador fixo junto ao header (popover com ícone)."""
    route = st.session_state.get("ui_route", "main")
    _inject_user_menu_header_css()

    if route != "main":
        if st.button("← Voltar à app", key="watty_top_voltar_app"):
            st.session_state.ui_route = "main"
            st.rerun()
        st.markdown(
            '<div class="watty-top-spacer-after-voltar" style="height:0.35rem"></div>',
            unsafe_allow_html=True,
        )

    nome_full = (
        st.session_state.get("nome_display")
        or st.session_state.get("nome_aluno")
        or "Conta"
    )
    nome_btn = _truncate_display_name(str(nome_full))
    with st.popover(
        nome_btn,
        icon="👤",
        use_container_width=True,
        key="watty_user_menu_popover",
    ):
        if st.button("Visualizar Perfil", key="watty_popover_perfil", use_container_width=True):
            st.session_state.ui_route = "perfil"
            st.rerun()
        if st.button("Log out", key="watty_popover_logout", use_container_width=True):
            logout_clear_session()
            st.rerun()


def render_guest_voltar_bar() -> None:
    if st.button("← Voltar ao início", key="watty_guest_voltar"):
        st.session_state.ui_route = "main"
        st.rerun()


def render_hud_metrics() -> None:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="👤 Jogador",
            value=st.session_state.get("nome_display") or st.session_state["nome_aluno"],
        )
    with col2:
        st.metric(label="🔰 Nível", value=f"Nvl {st.session_state.nivel}")
    with col3:
        st.metric(label="🏆 XP", value=f"{st.session_state.xp}")
    with col4:
        st.metric(label="🔥 Streak", value=f"{st.session_state.streak} Dias")
    st.markdown("---")


def render_sidebar():
    """Renderiza sidebar e devolve (ano_escolhido, disciplina_escolhida, aba_escolhida, exemplo_atual)."""
    try:
        st.sidebar.image(
            "Design_sem_nome__3_-removebg-preview.png",
            use_container_width=True,
        )
    except FileNotFoundError:
        st.sidebar.error(
            "⚠️ Imagem 'Design_sem_nome__3_-removebg-preview.png' não encontrada. "
            "Verifica as maiúsculas e minúsculas!"
        )

    st.sidebar.title("⚡ Menu do Watty")
    _ola = st.session_state.get("nome_display") or st.session_state.get("nome_aluno", "Pioneiro")
    st.sidebar.success(f"👤 Olá, {_ola}!")

    ano_escolhido = st.sidebar.selectbox("🎓 Escolhe o Ano:", LISTA_ANOS)

    lista_disciplinas = disciplinas_para_ano(ano_escolhido)
    disciplina_escolhida = st.sidebar.selectbox("📚 Escolhe a Disciplina:", lista_disciplinas)

    exemplo_atual = exemplo_para_disciplina(disciplina_escolhida)

    st.sidebar.markdown("---")
    aba_escolhida = st.sidebar.radio("O que queres fazer?", ABAS)

    return ano_escolhido, disciplina_escolhida, aba_escolhida, exemplo_atual


def render_login_footer_links() -> None:
    """Rodapé só no ecrã de login: texto com links sublinhados (navegação interna + externos)."""
    li = html.escape(FOOTER_URL_LINKEDIN, quote=True)
    mailto = f"mailto:{FOOTER_EMAIL_AJUDA}?subject={quote('Ajuda Watty')}"
    mailto_q = html.escape(mailto, quote=True)

    st.markdown(
        f"""
<nav class="watty-login-footer" aria-label="Informações e ligações">
  <a class="watty-login-footer__link" href="?watty_page=quem_somos">Quem Somos</a>
  <span class="watty-login-footer__sep" aria-hidden="true">|</span>
  <a class="watty-login-footer__link" href="?watty_page=termos">Termos e privacidade</a>
  <span class="watty-login-footer__sep" aria-hidden="true">|</span>
  <a class="watty-login-footer__link" href="{li}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
  <span class="watty-login-footer__sep" aria-hidden="true">|</span>
  <a class="watty-login-footer__link" href="{mailto_q}">Ajuda e Suporte</a>
</nav>
""",
        unsafe_allow_html=True,
    )
