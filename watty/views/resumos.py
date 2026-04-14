"""Aba Resumos."""

import streamlit as st

from watty.config import GEMINI_MODEL
from watty.prompts.common import REGRA_GRAFICOS
from watty.services.sheets import guardar_no_excel
from watty.utils.charts import exibir_com_graficos


def render_resumos_tab(
    client,
    ano_escolhido: str,
    disciplina_escolhida: str,
    exemplo_atual: str,
) -> None:
    st.title(f"📚 Máquina de Resumos: {disciplina_escolhida}")

    tema_resumo = st.text_input(
        f"O que precisas de resumir? (Ex: {exemplo_atual})"
    )

    if st.button("Criar Resumo Mágico 🪄"):
        if tema_resumo:
            with st.spinner("A processar resumo... 📚"):
                prompt_resumo = f"""
                Cria um resumo sobre {tema_resumo} focado no programa de {disciplina_escolhida} do {ano_escolhido}.
                Divide em: 1. O Conceito Central, 2. A Anatomia da Matéria, 3. Exemplo Prático, 4. Exceções, 5. Dica Ninja.

                {REGRA_GRAFICOS}
                """
                try:
                    resposta_resumo = client.models.generate_content(
                        model=GEMINI_MODEL, contents=prompt_resumo
                    )
                    exibir_com_graficos(resposta_resumo.text)

                    guardar_no_excel(
                        "Resumo",
                        tema_resumo,
                        resposta_resumo.text,
                        ano_escolhido,
                        disciplina_escolhida,
                    )

                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("Escreve um tema!")
