"""Layout principal: login, HUD, sidebar."""

import streamlit as st

from watty.config import LISTA_ANOS, disciplinas_para_ano, exemplo_para_disciplina
from watty.services.sheets import carregar_perfil

ABAS = ["💬 Chat Socrático", "🏋️ Treinar (Quizzes)", "📚 Aprender (Resumos)"]


def init_session_state() -> None:
    if "logado" not in st.session_state:
        st.session_state.logado = False


def render_login_gate() -> None:
    st.title("⚡ Bem-vindo ao Watty!")
    st.markdown("O teu tutor inteligente 24/7.")

    nome_input = st.text_input("Qual é o teu Nome e Turma? (Ex: João - 8ºB)")

    if st.button("Entrar no Jogo 🚀"):
        if nome_input.strip() != "":
            with st.spinner("A carregar o teu progresso na cloud... ☁️"):
                xp_bd, nivel_bd, streak_bd, linha_bd = carregar_perfil(nome_input)

                st.session_state.logado = True
                st.session_state["nome_aluno"] = nome_input
                st.session_state.xp = xp_bd
                st.session_state.nivel = nivel_bd
                st.session_state.streak = streak_bd
                st.session_state.linha_bd = linha_bd
                st.rerun()
        else:
            st.warning("⚠️ Epa, não te esqueças de escrever o teu nome!")


def render_hud_metrics() -> None:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="👤 Jogador", value=st.session_state["nome_aluno"])
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
    st.sidebar.success(f"👤 Olá, {st.session_state.get('nome_aluno', 'Pioneiro')}!")

    ano_escolhido = st.sidebar.selectbox("🎓 Escolhe o Ano:", LISTA_ANOS)

    lista_disciplinas = disciplinas_para_ano(ano_escolhido)
    disciplina_escolhida = st.sidebar.selectbox("📚 Escolhe a Disciplina:", lista_disciplinas)

    exemplo_atual = exemplo_para_disciplina(disciplina_escolhida)

    st.sidebar.markdown("---")
    aba_escolhida = st.sidebar.radio("O que queres fazer?", ABAS)

    return ano_escolhido, disciplina_escolhida, aba_escolhida, exemplo_atual
