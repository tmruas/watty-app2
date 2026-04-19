"""Página institucional Watty."""

from __future__ import annotations

import streamlit as st


def render_quem_somos_view() -> None:
    st.header("Quem somos")
    st.markdown(
        """
Bem-vindo ao Watty. ⚡
Nós não somos mais um livro de exercícios aborrecido. Somos o teu explicador particular alimentado por Inteligência Artificial, disfarçado de videojogo.

Nascemos com uma missão clara: acabar com a 'seca' de estudar para os Exames Nacionais. Aqui não há decorar à força. Há Boss Battles, treinos táticos e Rankings Globais.

Errar faz parte do jogo, e nós estamos aqui para garantir que sobes de nível até chegares ao 20.

Estás pronto para jogar?
        """.strip()
    )
