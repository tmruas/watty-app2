import io
import re

import pandas as pd
import streamlit as st


def exibir_com_graficos(texto_ia: str) -> None:
    """Procura por dados de gráficos na resposta e desenha-os; o resto em markdown."""
    padrao = r"\[GRAFICO\](.*?)\[/GRAFICO\]"
    partes = re.split(padrao, texto_ia, flags=re.DOTALL)

    for i, parte in enumerate(partes):
        if i % 2 == 0:
            if parte.strip():
                st.markdown(parte)
        else:
            try:
                dados_csv = parte.strip()
                df = pd.read_csv(io.StringIO(dados_csv))
                if len(df.columns) > 0:
                    df.set_index(df.columns[0], inplace=True)
                st.line_chart(df)
            except Exception:
                st.error("⚠️ [Erro ao processar o gráfico gerado pela IA]")
