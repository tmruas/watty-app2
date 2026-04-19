"""Ponto de entrada Streamlit — Watty.

Antes do primeiro `streamlit run`, compila o onboarding React:
`cd watty_login_wizard/frontend && npm ci && npm run build`
(ver README.md).

Requer segredos Supabase para o login (`SUPABASE_*` em `.streamlit/secrets.toml`; ver GUIA_EXECUCAO.md).
"""

import streamlit as st

from watty.services.auth_session import try_restore_session_from_cookies
from watty.services.gemini import get_gemini_client, init_gemini_from_secrets
from watty.ui.layout import (
    init_session_state,
    render_app_top_bar,
    render_guest_voltar_bar,
    render_hud_metrics,
    render_login_footer_links,
    render_login_gate,
    render_sidebar,
    sync_footer_nav_from_query_params,
)
from watty.ui.styles import inject_global_styles
from watty.views.chat import render_chat_tab
from watty.views.jogos import get_active_game_filename, render_jogos_library, render_jogos_player
from watty.views.watty_tv import render_watty_tv
from watty.views.perfil import render_perfil_view
from watty.views.quem_somos import render_quem_somos_view
from watty.views.quiz import render_quiz_tab
from watty.views.resumos import render_resumos_tab
from watty.views.termos import render_termos_view

st.set_page_config(
    page_title="Watty | O teu Tutor Inteligente",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_gemini_from_secrets()
inject_global_styles()
init_session_state()
try_restore_session_from_cookies()
sync_footer_nav_from_query_params()

route = st.session_state.get("ui_route", "main")

# Visitante: páginas estáticas sem login
if not st.session_state.logado and route in ("quem_somos", "termos"):
    render_guest_voltar_bar()
    if route == "quem_somos":
        render_quem_somos_view()
    else:
        render_termos_view()
    st.stop()

if not st.session_state.logado:
    render_login_gate()
    render_login_footer_links()
    st.stop()

# Autenticado: barra superior (menu + voltar em rotas auxiliares)
render_app_top_bar()

# Rotas auxiliares (perfil / institucional / termos)
if route == "perfil":
    render_perfil_view()
    st.stop()
if route == "quem_somos":
    render_quem_somos_view()
    st.stop()
if route == "termos":
    render_termos_view()
    st.stop()

render_hud_metrics()

client = get_gemini_client()
ano_escolhido, disciplina_escolhida, main_section, exemplo_atual = render_sidebar()

_active_game = get_active_game_filename()
if _active_game:
    render_jogos_player(_active_game)
    st.stop()

if main_section == "jogos":
    render_jogos_library()
    st.stop()

if main_section == "watty_tv":
    render_watty_tv()
    st.stop()

if main_section == "chat":
    render_chat_tab(client, ano_escolhido, disciplina_escolhida)
elif main_section == "quiz":
    render_quiz_tab(client, ano_escolhido, disciplina_escolhida, exemplo_atual)
elif main_section == "resumos":
    render_resumos_tab(client, ano_escolhido, disciplina_escolhida, exemplo_atual)
