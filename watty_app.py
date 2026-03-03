import streamlit as st
import os
from google import genai
from PIL import Image # Necessário para processar a imagem

# --- 1. A TUA CHAVE DE ACESSO ---
# Certifica-te que a chave está nos st.secrets do Streamlit
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

# --- NOVO: SELETOR DE ANO ---
lista_anos = ["8º Ano", "9º Ano", "10º Ano", "11º Ano", "12º Ano"]
ano_escolhido = st.sidebar.selectbox("🎓 Escolhe o Ano:", lista_anos)

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
exemplo_atual = exemplos[disciplina_escolhida]
st.sidebar.markdown("---")

aba_escolhida = st.sidebar.radio("O que queres fazer?", ["💬 Chat Socrático", "🏋️ Treinar (Quizzes)", "📚 Aprender (Resumos)"])

# --- 4. A ABA DO CHAT (COM VISÃO) ---
if aba_escolhida == "💬 Chat Socrático":
    st.title(f"💬 O Super Tutor de {disciplina_escolhida}")
    st.write(f"Pergunta-me algo ou envia uma foto do teu exercício!")

    # --- NOVO: UPLOAD DE IMAGEM ---
    foto_exercicio = st.file_uploader("📸 Envia uma foto do exercício (opcional)", type=["jpg", "jpeg", "png"])
    
    if foto_exercicio:
        imagem_pil = Image.open(foto_exercicio)
        st.image(imagem_pil, caption="Imagem carregada!", width=300)

    chave_memoria = f"mensagens_{disciplina_escolhida}" 

    if chave_memoria not in st.session_state:
        st.session_state[chave_memoria] = [{"role": "assistant", "content": f"Olá! ⚡ Sou o teu tutor de {disciplina_escolhida}. Que desafio vamos resolver hoje?"}]

    # Mostrar histórico
    for msg in st.session_state[chave_memoria]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    mensagem_aluno = st.chat_input("Escreve a tua dúvida aqui...")

    if mensagem_aluno:
        # 1. Mostrar mensagem do aluno
        with st.chat_message("user"):
            st.markdown(mensagem_aluno)
        st.session_state[chave_memoria].append({"role": "user", "content": mensagem_aluno})

        # 2. Resposta da IA
        with st.chat_message("assistant"):
            prompt_secreto = f"""
És o Watty, um tutor genial e muito energético especializado em {disciplina_escolhida} do {ano_escolhido} em Portugal.
O teu objetivo não é dar a resposta logo, mas sim fazer o aluno pensar!

REGRAS DE OURO:
1. FOCO NO ANO: Adequa rigorosamente o teu vocabulário, os métodos de resolução e a profundidade científica ao programa oficial do {ano_escolhido} (Aprendizagens Essenciais). Nunca utilizes conceitos matemáticos ou científicos de anos letivos seguintes!
2. SOCRÁTICO: Não dês a resposta final. Dá pequenas dicas e faz perguntas guiadas para o aluno chegar lá sozinho. Dá apenas a resposta quando o aluno demonstra frustração.
3. VISÃO: Se o aluno enviar uma imagem, analisa o exercício e ajuda-o a decifrar o enunciado passo a passo.
Sê motivador, divertido e usa emojis! ⚡
"""
            
            # Construir a lista de conteúdos para a API (Texto + Imagem se houver)
            conteudo_para_ia = [prompt_secreto]
            
            # Adicionar histórico curto (últimas 4 mensagens para poupar tokens)
            mensagens_recentes = st.session_state[chave_memoria][-4:]
            for m in mensagens_recentes:
                conteudo_para_ia.append(f"{m['role']}: {m['content']}")
            
            # Adicionar a imagem se ela existir
            if foto_exercicio:
                conteudo_para_ia.append(imagem_pil)
            
            # Adicionar a pergunta atual
            conteudo_para_ia.append(f"Pergunta atual do aluno: {mensagem_aluno}")

            try:
                # Usamos o modelo 1.5-flash que é excelente com imagens
                resposta_ia = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=conteudo_para_ia
                )
                st.markdown(resposta_ia.text)
                st.session_state[chave_memoria].append({"role": "assistant", "content": resposta_ia.text})
            except Exception as e:
                st.error(f"Erro na IA: {e}")

# --- 5. A ABA DE TREINAR (QUIZZES) ---
elif aba_escolhida == "🏋️ Treinar (Quizzes)":
    st.title(f"🏋️ Fábrica de Exercícios: {disciplina_escolhida}")
    
    tema_exercicios = st.text_input(f"Qual é o tema que queres treinar? (Ex: {exemplo_atual})")
    
    if st.button("Gerar Exercícios ⚙️"):
        if tema_exercicios:
            with st.spinner("O Watty está a construir os exercícios... 🛠️"):
                prompt_treino = f"""
És o Watty, o tutor de elite para alunos em Portugal.
Cria um teste rigoroso de 5 perguntas sobre: {tema_exercicios}.

REGRAS OBRIGATÓRIAS (Lê com atenção!):
1. FOCO NO PROGRAMA: Os exercícios têm de ser EXCLUSIVAMENTE focados na matéria de {disciplina_escolhida} do {ano_escolhido} (segundo as Aprendizagens Essenciais de Portugal). Não incluas conceitos de anos mais avançados!
2. DIFICULDADE DE EXAME: A dificuldade deve ser ao nível de uma questão de Exame Nacional, Teste Intermédio ou de um teste final de período muito exigente para o {ano_escolhido}.
3. DIVERSIDADE: Inclui 3 perguntas de Escolha Múltipla e 2 Perguntas Abertas (de desenvolvimento ou cálculo).
4. ALEATORIEDADE: Nas perguntas de escolha múltipla, a opção correta TEM de ser distribuída de forma totalmente aleatória entre A, B, C e D.
"""
                try:
                    resposta_treino = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_treino)
                    st.markdown(resposta_treino.text)
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("Escreve um tema!")

# --- 6. A ABA DE APRENDER (RESUMOS) ---
elif aba_escolhida == "📚 Aprender (Resumos)":
    st.title(f"📚 Máquina de Resumos: {disciplina_escolhida}")
    
    tema_resumo = st.text_input(f"O que precisas de resumir? (Ex: {exemplo_atual})")
    
    if st.button("Criar Resumo Mágico 🪄"):
        if tema_resumo:
            with st.spinner("A processar resumo... 📚"):
                prompt_resumo = f"""
És o Watty, um tutor genial e super detalhista de {disciplina_escolhida} do secundário e 3º ciclo em Portugal.
O teu objetivo é criar um resumo sobre o tema: {tema_resumo}.

REGRAS VITAIS:
1. LIMITES DO PROGRAMA: Explica a matéria de forma completa, mas ESTRITAMENTE LIMITADA ao que se exige no programa oficial do {ano_escolhido}. Se o tema existir em vários anos (ex: Geometria), foca-te apenas no que se dá no {ano_escolhido}.
2. FORMATO DE PARTES: Divide a tua resposta em "Partes" visuais para não cansar a vista do aluno.
3. VISUAL: Usa tabelas Markdown, blocos de nota (com o símbolo >), negritos e muitos emojis.

Usa EXATAMENTE esta estrutura:

# 🟦 1: O Conceito Central
(Explica o que é e dá a definição oficial exigida para o {ano_escolhido})
---

# 🟦 2: A Anatomia da Matéria
(A teoria completa, fórmulas, datas ou regras - adaptadas ao {ano_escolhido}. Usa tabelas se ajudar!)
---

# 🟦 3: Exemplo Prático / Aplicação
(Mostra como isto costuma aparecer num teste normal do {ano_escolhido} e resolve passo a passo)
---

# 🟦 4: Exceções e Rasteiras
(Quais são as "rasteiras" clássicas que os professores de {ano_escolhido} adoram pôr nos testes sobre isto?)
---

# 🟦 5: A Dica Ninja do Watty ⚡
(Uma técnica de memorização, um truque para decorar ou um resumo de 1 frase).
"""
                try:
                    resposta_resumo = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_resumo)
                    st.markdown(resposta_resumo.text)
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("Escreve um tema!")



