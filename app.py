"""Ponto de entrada Streamlit — Watty.

Antes do primeiro `streamlit run`, compila o onboarding React:
`cd watty_login_wizard/frontend && npm ci && npm run build`
(ver README.md).
"""

import streamlit as st

from watty.services.gemini import get_gemini_client, init_gemini_from_secrets
from watty.ui.layout import (
    init_session_state,
    render_hud_metrics,
    render_login_gate,
    render_sidebar,
)
from watty.ui.styles import inject_global_styles
from watty.views.chat import render_chat_tab
from watty.views.quiz import render_quiz_tab
from watty.views.resumos import render_resumos_tab

st.set_page_config(
    page_title="Watty | O teu Tutor Inteligente",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_gemini_from_secrets()
inject_global_styles()
init_session_state()

if not st.session_state.logado:
    render_login_gate()
    st.stop()

render_hud_metrics()

client = get_gemini_client()
ano_escolhido, disciplina_escolhida, aba_escolhida, exemplo_atual = render_sidebar()

if aba_escolhida == "💬 Chat Socrático":
    render_chat_tab(client, ano_escolhido, disciplina_escolhida)
elif aba_escolhida == "🏋️ Treinar (Quizzes)":
    render_quiz_tab(client, ano_escolhido, disciplina_escolhida, exemplo_atual)
elif aba_escolhida == "📚 Aprender (Resumos)":
    render_resumos_tab(client, ano_escolhido, disciplina_escolhida, exemplo_atual)
