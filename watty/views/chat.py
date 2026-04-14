"""Aba Chat Socrático."""

from PIL import Image
import streamlit as st

from watty.config import GEMINI_MODEL
from watty.prompts.chat_prompts import build_chat_system_prompt
from watty.services.sheets import guardar_no_excel
from watty.utils.charts import exibir_com_graficos

CHAT_SKELETON_HTML = """
<div class="watty-chat-skeleton" aria-busy="true" aria-live="polite">
    <div class="watty-sk-line watty-sk-w100"></div>
    <div class="watty-sk-line watty-sk-w85"></div>
    <div class="watty-sk-line watty-sk-w95"></div>
    <div class="watty-sk-line watty-sk-w60"></div>
</div>
"""


def render_chat_tab(client, ano_escolhido: str, disciplina_escolhida: str) -> None:
    st.title(f"💬 O Super Tutor de {disciplina_escolhida}")
    st.write("Pergunta-me algo ou envia uma foto do teu exercício!")

    foto_exercicio = st.file_uploader(
        "📸 Envia uma foto do exercício (opcional)", type=["jpg", "jpeg", "png"]
    )

    imagem_pil = None
    if foto_exercicio:
        imagem_pil = Image.open(foto_exercicio)
        st.image(imagem_pil, caption="Imagem carregada!", width=300)

    chave_memoria = f"mensagens_{ano_escolhido}_{disciplina_escolhida}"

    if chave_memoria not in st.session_state:
        st.session_state[chave_memoria] = [
            {
                "role": "assistant",
                "content": f"Olá! ⚡ Sou o teu tutor de {disciplina_escolhida}. Que desafio vamos resolver hoje?",
            }
        ]

    for msg in st.session_state[chave_memoria]:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                exibir_com_graficos(msg["content"])
            else:
                st.markdown(msg["content"])

    mensagem_aluno = st.chat_input("Escreve a tua dúvida aqui...")

    if mensagem_aluno:
        with st.chat_message("user"):
            st.markdown(mensagem_aluno)
        st.session_state[chave_memoria].append(
            {"role": "user", "content": mensagem_aluno}
        )

        with st.chat_message("assistant"):
            placeholder_resposta = st.empty()
            placeholder_resposta.markdown(CHAT_SKELETON_HTML, unsafe_allow_html=True)

            prompt_secreto = build_chat_system_prompt(disciplina_escolhida, ano_escolhido)

            conteudo_para_ia = [prompt_secreto]

            mensagens_recentes = st.session_state[chave_memoria][-4:]
            for m in mensagens_recentes:
                conteudo_para_ia.append(f"{m['role']}: {m['content']}")

            if imagem_pil:
                conteudo_para_ia.append(imagem_pil)

            conteudo_para_ia.append(f"Pergunta do aluno: {mensagem_aluno}")

            try:
                resposta_ia = client.models.generate_content(
                    model=GEMINI_MODEL, contents=conteudo_para_ia
                )
                placeholder_resposta.empty()
                exibir_com_graficos(resposta_ia.text)
                st.session_state[chave_memoria].append(
                    {"role": "assistant", "content": resposta_ia.text}
                )

                guardar_no_excel(
                    "Chat",
                    mensagem_aluno,
                    resposta_ia.text,
                    ano_escolhido,
                    disciplina_escolhida,
                )

            except Exception as e:
                placeholder_resposta.empty()
                st.error(f"Erro na IA: {e}")
