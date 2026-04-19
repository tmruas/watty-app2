"""Termos e privacidade (texto-base; revisão legal recomendada antes de produção)."""

from __future__ import annotations

import streamlit as st


def render_termos_view() -> None:
    st.header("Termos e privacidade")
    st.markdown(
        """
### Utilização do serviço

Ao utilizares a aplicação Watty, comprometes-te a usar o serviço de forma responsável e de acordo
com as leis aplicáveis. O conteúdo gerado por IA é informativo e pedagógico; não substitui
orientação de professores, manuais oficiais nem aconselhamento profissional.

### Dados pessoais

Tratamos o mínimo de dados necessários para autenticação (por exemplo, email via Supabase) e para
o teu progresso na plataforma (por exemplo, identificação na folha de perfil). Consulta a política
do teu estabelecimento de ensino e as leis de proteção de dados (RGPD) aplicáveis ao tratamento.

### Contacto

Para questões sobre estes termos ou sobre dados: usa o contacto de **Ajuda e Suporte** no rodapé
da aplicação.

---
*Este texto é um modelo genérico. Deve ser revisto por aconselhamento jurídico antes de uso público.*
        """.strip()
    )
