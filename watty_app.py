import streamlit as st
import os
from google import genai

# --- 1. A TUA CHAVE DE ACESSO ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
client = genai.Client()

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Watty | O teu Tutor Inteligente", page_icon="⚡", layout="centered")

# --- 3. MENU LATERAL (A Bússola) ---
st.sidebar.image("https://api.dicebear.com/7.x/bottts/svg?seed=Watty&backgroundColor=1CB0F6", width=100)
st.sidebar.title("⚡ Menu do Watty")

lista_disciplinas = [
    "Matemática", "Português", "Economia", "Físico-Química", 
    "Filosofia", "Biologia", "História", "MACS", "Geometria Descritiva"
]
disciplina_escolhida = st.sidebar.selectbox("📚 Escolhe a Disciplina:", lista_disciplinas)
# --- O Dicionário de Exemplos ---
exemplos = {
    "Matemática": "Limites, Trigonometria",
    "Português": "Os Lusíadas, Fernando Pessoa",
    "Economia": "Inflação, Lei da Oferta e Procura",
    "Físico-Química": "Leis de Newton, Tabela Periódica",
    "Filosofia": "Lógica, Kant",
    "Biologia": "Mitose, Genética",
    "História": "Revolução Francesa, Estado Novo",
    "MACS": "Grafos, Probabilidades",
    "Geometria Descritiva": "Projeções, Sombras"
}
# Apanhamos o exemplo certo para a disciplina escolhida
exemplo_atual = exemplos[disciplina_escolhida]
st.sidebar.markdown("---")

aba_escolhida = st.sidebar.radio("O que queres fazer?", ["💬 Chat Socrático", "🏋️ Treinar (Quizzes)", "📚 Aprender (Resumos)"])


# --- 4. A ABA DO CHAT ---
if aba_escolhida == "💬 Chat Socrático":
    st.title(f"💬 O Super Tutor de {disciplina_escolhida}")
    st.write(f"Pergunta-me qualquer coisa sobre {disciplina_escolhida}!")

    # O GRANDE TRUQUE: Criar um nome de gaveta único para cada disciplina!
    chave_memoria = f"mensagens_{disciplina_escolhida}" 

    # Se a gaveta desta disciplina específica ainda não existir, criamos uma!
    if chave_memoria not in st.session_state:
        st.session_state[chave_memoria] = [{"role": "assistant", "content": f"Olá, Construtor! ⚡ Que mistério de {disciplina_escolhida} vamos resolver hoje?"}]

    # Mostramos apenas as mensagens guardadas na gaveta da disciplina atual
    for msg in st.session_state[chave_memoria]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    mensagem_aluno = st.chat_input("Escreve a tua dúvida aqui...")

    if mensagem_aluno:
        with st.chat_message("user"):
            st.markdown(mensagem_aluno)
        # Guardamos a pergunta na gaveta certa
        st.session_state[chave_memoria].append({"role": "user", "content": mensagem_aluno})

        with st.chat_message("assistant"):
            prompt_secreto = f"""
            És o Watty, um tutor genial e muito energético especializado em {disciplina_escolhida} do ensino secundário em Portugal.
            O teu objetivo não é dar a resposta logo, mas sim fazer o aluno pensar!
            Dá pequenas dicas e faz perguntas guiadas. Sê divertido!
            """
            resposta_ia = client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=f"{prompt_secreto}\n\nAluno: {mensagem_aluno}"
            )
            st.markdown(resposta_ia.text)
            # Guardamos a resposta na gaveta certa
            st.session_state[chave_memoria].append({"role": "assistant", "content": resposta_ia.text})

# --- 5. A ABA DE TREINAR ---
elif aba_escolhida == "🏋️ Treinar (Quizzes)":
    st.title(f"🏋️ Fábrica de Exercícios: {disciplina_escolhida}")
    
    # AQUI ESTAVA O ERRO! Substituímos o texto fixo pelo {exemplo_atual}
    tema_exercicios = st.text_input(f"Qual é o tema de {disciplina_escolhida} que queres treinar? (Ex: {exemplo_atual})")
    
    if st.button("Gerar Exercícios ⚙️"):
        if tema_exercicios:
            with st.spinner("O Watty está a construir os exercícios na fábrica... 🛠️"):
                prompt_treino = f"""
                És o Watty, um tutor genial de {disciplina_escolhida} do secundário em Portugal.
                Cria um teste rápido de 5 perguntas de escolha múltipla sobre: {tema_exercicios}.
                No final do teste, fornece a chave de respostas e uma breve explicação para cada uma.
                """
                resposta_treino = client.models.generate_content(model='gemini-2.0-flash-lite', contents=prompt_treino)
                st.markdown(resposta_treino.text)
        else:
            st.warning("Por favor, escreve um tema primeiro!")
            
# --- 6. A ABA DE APRENDER ---
elif aba_escolhida == "📚 Aprender (Resumos)":
    st.title(f"📚 Máquina de Resumos: {disciplina_escolhida}")
    
    # A caixa de texto (já com o exemplo inteligente!)
    tema_resumo = st.text_input(f"Que matéria de {disciplina_escolhida} precisas de resumir? (Ex: {exemplo_atual})")
    
    if st.button("Criar Resumo Mágico 🪄"):
        if tema_resumo:
            # A animação de carregar (que tinha desaparecido)
            with st.spinner("O Watty está a processar os livros todos... 📚"):
                
                # O Novo Cérebro dos Resumos (Estilo Slides)
                prompt_resumo = f"""
                És o Watty, um tutor genial e super detalhista de {disciplina_escolhida} do secundário em Portugal.
                O teu objetivo é criar um resumo sobre o tema: {tema_resumo}.
                
                REGRAS VITAIS:
                1. A MATÉRIA TODA: Não dês apenas um resumo superficial. Explica a matéria de forma completa, com todo o rigor exigido nos exames nacionais.
                2. FORMATO DE SLIDES: Divide a tua resposta em "Slides" visuais para não cansar a vista do aluno.
                3. VISUAL: Usa tabelas Markdown, blocos de nota (com o símbolo >), negritos e muitos emojis.
                
                Usa EXATAMENTE esta estrutura:
                
                # 🟦 1: O Conceito Central
                (Explica o que é, o contexto e a definição oficial)
                ---
                
                # 🟦 2: A Anatomia da Matéria
                (A teoria completa, fórmulas, datas, causas/consequências ou regras gramaticais - usa tabelas se ajudar!)
                ---
                
                # 🟦 3: Exemplo Prático / Aplicação
                (Mostra como isto aparece num teste ou resolve um exercício passo a passo)
                ---
                
                # 🟦 4: Exceções e Rasteiras
                (Quais são as "rasteiras" clássicas que os professores põem nos testes sobre isto?)
                ---
                
                # 🟦 5: A Dica Ninja do Watty ⚡
                (Uma mnemónica, um truque para decorar ou um resumo de 1 frase).
                """
                
                # A linha que estava cortada, agora inteira!
                resposta_resumo = client.models.generate_content(
                    model='gemini-2.0-flash-lite', 
                    contents=prompt_resumo
                )
                
                st.markdown(resposta_resumo.text)
        else:

            st.warning("Por favor, escreve um tema!")









