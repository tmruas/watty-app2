"""Ecrã de perfil do utilizador autenticado."""

from __future__ import annotations

import streamlit as st


def render_perfil_view() -> None:
    st.header("O teu perfil")
    nome = st.session_state.get("nome_display") or ""
    email = st.session_state.get("nome_aluno") or ""
    st.markdown(f"**Nome:** {nome or '—'}")
    st.markdown(f"**Email:** {email or '—'}")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("XP", st.session_state.get("xp", 0))
    with c2:
        st.metric("Nível", st.session_state.get("nivel", 1))
    with c3:
        st.metric("Streak (dias)", st.session_state.get("streak", 0))
    st.caption("O progresso detalhado continua a ser guardado na nuvem (Google Sheets).")
