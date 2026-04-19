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
from watty.paths import watty_logosuperior_path, watty_sidebar_width_px
from watty.services.auth_session import (
    clear_skip_restore_after_login,
    logout_clear_session,
    save_auth_tokens_to_cookies,
)
from watty.services.sheets import carregar_perfil
from watty.services.supabase_auth import get_user_email_and_metadata
from watty.views.jogos import get_active_game_filename
from watty_login_wizard import render_login_wizard


def _inject_watty_sidebar_chrome(sidebar_w: int, main_section: str) -> None:
    """Largura da sidebar (logo) + estado ativo (paleta roxa Watty).

    O CSS é injetado com ``st.markdown`` na área principal (não ``st.sidebar``)
    para não ocupar espaço vertical no topo da sidebar como um espaçador.
    """
    active_class = {
        "chat": "st-key-watty_nav_aprender",
        "quiz": "st-key-watty_nav_treinar",
        "resumos": "st-key-watty_nav_resumos",
        "jogos": "st-key-watty_nav_jogos",
        "watty_tv": "st-key-watty_nav_watty_tv",
    }.get(main_section, "st-key-watty_nav_aprender")
    sidebar_rem = f"{(sidebar_w / 16.0):.4f}".rstrip("0").rstrip(".")
    st.markdown(
        f"""
<style>
@media (min-width: 769px) {{
    section[data-testid="stSidebar"] {{
        width: {sidebar_rem}rem !important;
        min-width: {sidebar_rem}rem !important;
        max-width: {sidebar_rem}rem !important;
    }}
}}
@media (max-width: 768px) {{
    section[data-testid="stSidebar"] {{
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }}
}}
section[data-testid="stSidebar"] div.element-container.{active_class} button {{
    background-color: #F3E5F5 !important;
    color: #6A1B9A !important;
    border: 0.125rem solid #9C27B0 !important;
    border-radius: 0.75rem !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] div.element-container.{active_class} button:hover {{
    background-color: #E1BEE7 !important;
    color: #4A148C !important;
    border-color: #7B1FA2 !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    if "logado" not in st.session_state:
        st.session_state.logado = False
    if "ui_route" not in st.session_state:
        st.session_state.ui_route = "main"
    if "watty_main_section" not in st.session_state:
        st.session_state.watty_main_section = "chat"


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
        email, meta, created_at = get_user_email_and_metadata(
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
        st.session_state["user_created_at"] = created_at
    rt = str(resultado.get("refresh_token", "") or "").strip()
    if rt:
        save_auth_tokens_to_cookies(token, rt)
    clear_skip_restore_after_login()
    st.rerun()


def _abbr_profile_display_name(full: str) -> str:
    """Nome abreviado para o cartão de perfil (ex.: 'Ana Maria Santos Silva' -> 'A. M. Santos Silva')."""
    parts = [p for p in (full or "").strip().split() if p]
    if not parts:
        return "Conta"
    if len(parts) >= 4:
        a = (parts[0][0] if parts[0] else "").upper()
        b = (parts[1][0] if parts[1] else "").upper()
        rest = " ".join(parts[2:])
        return f"{a}. {b}. {rest}".strip()
    if len(parts) == 3:
        a = (parts[0][0] if parts[0] else "").upper()
        rest = " ".join(parts[1:])
        return f"{a}. {rest}".strip()
    if len(parts) == 2:
        a = (parts[0][0] if parts[0] else "").upper()
        return f"{a}. {parts[1]}"
    n0 = parts[0]
    return n0 if len(n0) <= 26 else n0[:25] + "…"


def render_app_top_bar() -> None:
    """Voltar (em rotas auxiliares) + cartão de perfil no topo direito da área principal (popover)."""
    route = st.session_state.get("ui_route", "main")

    st.markdown(
        """
<style>
/* Linha do topo: coluna do popover de perfil alinhada à direita da área principal */
div[data-testid="stHorizontalBlock"]:has(.st-key-watty_profile_bar)
    > div[data-testid="column"]:last-child {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}
</style>
""",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([6, 1])
    with col_left:
        if route != "main":
            if st.button("← Voltar à app", key="watty_top_voltar_app"):
                st.session_state.ui_route = "main"
                st.rerun()
            st.markdown(
                '<div class="watty-top-spacer-after-voltar" style="height:0.35rem"></div>',
                unsafe_allow_html=True,
            )

    with col_right:
        nome_full = (
            st.session_state.get("nome_display")
            or st.session_state.get("nome_aluno")
            or "Conta"
        )
        nome_perfil = _abbr_profile_display_name(str(nome_full))
        rotulo_perfil = f"{nome_perfil}\u00a0▾"
        with st.popover(
            rotulo_perfil,
            icon=":material/account_circle:",
            type="secondary",
            width="content",
            key="watty_profile_bar",
        ):
            if st.button("Visualizar Perfil", key="watty_popover_perfil", use_container_width=True):
                st.session_state.ui_route = "perfil"
                st.rerun()
            if st.button("Log out", key="watty_popover_logout", use_container_width=True):
                logout_clear_session()


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
    """Renderiza sidebar e devolve (ano_escolhido, disciplina_escolhida, main_section, exemplo_atual).

    ``main_section`` é um id estável: ``chat`` | ``quiz`` | ``resumos`` | ``jogos`` | ``watty_tv``.
    """
    raw = st.session_state.get("watty_main_section", "chat")
    if raw not in ("chat", "quiz", "resumos", "jogos", "watty_tv"):
        st.session_state.watty_main_section = "chat"
    main_section = st.session_state.watty_main_section
    nav_highlight = "jogos" if get_active_game_filename() else main_section

    logo_path = watty_logosuperior_path()
    sidebar_w = watty_sidebar_width_px(logo_path) if logo_path.is_file() else 280
    _inject_watty_sidebar_chrome(sidebar_w, nav_highlight)

    if logo_path.is_file():
        st.sidebar.image(str(logo_path), use_container_width=True)
    else:
        st.sidebar.error(
            "⚠️ Logo não encontrado. Na raiz do projeto usa um destes nomes: "
            "`watty_logosuperior.jpeg`, `watty_logosuperior.jpg` ou `watty_logosuperior.png`."
        )

    st.sidebar.markdown("### Menu do Watty")
    _ola = st.session_state.get("nome_display") or st.session_state.get("nome_aluno", "Pioneiro")
    st.sidebar.success(f"👤 Olá, {_ola}!")

    ano_escolhido = st.sidebar.selectbox("🎓 Escolhe o Ano:", LISTA_ANOS)

    lista_disciplinas = disciplinas_para_ano(ano_escolhido)
    disciplina_escolhida = st.sidebar.selectbox("📚 Escolhe a Disciplina:", lista_disciplinas)

    exemplo_atual = exemplo_para_disciplina(disciplina_escolhida)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<p class="watty-sidebar-section-title">O que queres fazer?</p>',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "Aprender",
        key="watty_nav_aprender",
        use_container_width=True,
        type="primary" if nav_highlight == "chat" else "secondary",
        icon=":material/school:",
    ):
        st.session_state.watty_main_section = "chat"
        try:
            del st.query_params["watty_game"]
        except Exception:
            pass
        st.rerun()

    if st.sidebar.button(
        "Treinar",
        key="watty_nav_treinar",
        use_container_width=True,
        type="primary" if nav_highlight == "quiz" else "secondary",
        icon=":material/fitness_center:",
    ):
        st.session_state.watty_main_section = "quiz"
        try:
            del st.query_params["watty_game"]
        except Exception:
            pass
        st.rerun()

    if st.sidebar.button(
        "Resumos",
        key="watty_nav_resumos",
        use_container_width=True,
        type="primary" if nav_highlight == "resumos" else "secondary",
        icon=":material/menu_book:",
    ):
        st.session_state.watty_main_section = "resumos"
        try:
            del st.query_params["watty_game"]
        except Exception:
            pass
        st.rerun()

    if st.sidebar.button(
        "Watty TV",
        key="watty_nav_watty_tv",
        use_container_width=True,
        type="primary" if nav_highlight == "watty_tv" else "secondary",
        icon=":material/smart_display:",
    ):
        st.session_state.watty_main_section = "watty_tv"
        try:
            del st.query_params["watty_game"]
        except Exception:
            pass
        st.rerun()

    if st.sidebar.button(
        "Jogos",
        key="watty_nav_jogos",
        use_container_width=True,
        type="primary" if nav_highlight == "jogos" else "secondary",
        icon=":material/sports_esports:",
    ):
        st.session_state.watty_main_section = "jogos"
        try:
            del st.query_params["watty_game"]
        except Exception:
            pass
        st.rerun()

    st.sidebar.button(
        "Ranking\nem breve",
        key="watty_nav_ranking",
        use_container_width=True,
        disabled=True,
        icon=":material/lock:",
    )

    return ano_escolhido, disciplina_escolhida, main_section, exemplo_atual


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
