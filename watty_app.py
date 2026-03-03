import streamlit as st
import os
from google import genai
from PIL import Image

# --- 1. A TUA CHAVE DE ACESSO ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
client = genai.Client()

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Watty | O teu Tutor Inteligente", page_icon="⚡", layout="centered")

# --- 3. MENU LATERAL (A Bússola) ---
st.sidebar.image("https://api.dicebear.com/7.x/bottts/svg?seed=Watty&backgroundColor=1CB0F6", width=100)
st.sidebar.title("⚡ Menu do Watty")

# 1º PASSO: Escolher o Ano PRIMEIRO
lista_anos = ["8º Ano", "9º Ano", "10º Ano", "11º Ano", "12º Ano"]
ano_escolhido = st.sidebar.selectbox("🎓 Escolhe o Ano:", lista_anos)

# 2º PASSO: A lista de disciplinas muda conforme o ano
if ano_escolhido in ["8º Ano", "9º Ano"]:
    lista_disciplinas = [
        "Matemática", "Português", "Físico-Química", "Ciências Naturais", 
        "História", "Geografia", "Inglês"
    ]
else:
    lista_disciplinas = [
        "Matemática A", "Matemática B", "MACS", "Português", "Economia", 
        "Físico-Química", "Filosofia", "Biologia e Geologia", "História A", 
        "Geometria Descritiva"
    ]

# 3º PASSO: Escolher a Disciplina
disciplina_escolhida = st.sidebar.selectbox("📚 Escolhe a Disciplina:", lista_disciplinas)

exemplos = {
    "Matemática": "Teorema de Pitágoras, Equações",
    "Matemática A": "Limites, Trigonometria",
    "Matemática B": "Estatística, Taxa de Variação",
    "MACS": "Grafos, Probabilidades",
    "Português": "Os Lusíadas, Fernando Pessoa",
    "Economia": "Inflação, Procura e Oferta",
    "Físico-Química": "Leis de Newton, Tabela Periódica",
    "Ciências Naturais": "Sistema Digestivo, Fotossíntese",
    "Filosofia": "Lógica, Descartes",
    "Biologia e Geologia": "Mitose, Rochas Sedimentares",
    "História": "Revolução Francesa, 1ª Guerra Mundial",
    "História A": "Estado Novo, Guerra Fria",
    "Geografia": "Climas, Demografia",
    "Inglês": "Past Simple, Phrasal Verbs",
    "Geometria Descritiva": "Projeções, Sombras"
}

exemplo_atual = exemplos.get(disciplina_escolhida, "Tema da matéria")

st.sidebar.markdown("---")
aba_escolhida = st.sidebar.radio("O que queres fazer?", ["💬 Chat Socrático", "🏋️ Treinar (Quizzes)", "📚 Aprender (Resumos)"])

# --- 4. A ABA DO CHAT (COM VISÃO) ---
if aba_escolhida == "💬 Chat Socrático":
    st.title(f"💬 O Super Tutor de {disciplina_escolhida}")
    st.write("Pergunta-me algo ou envia uma foto do teu exercício!")

    foto_exercicio = st.file_uploader("📸 Envia uma foto do exercício (opcional)", type=["jpg", "jpeg", "png"])
    
    imagem_pil = None
    if foto_exercicio:
        imagem_pil = Image.open(foto_exercicio)
        st.image(imagem_pil, caption="Imagem carregada!", width=300)

    chave_memoria = f"mensagens_{ano_escolhido}_{disciplina_escolhida}" 

    if chave_memoria not in st.session_state:
        st.session_state[chave_memoria] = [{"role": "assistant", "content": f"Olá! ⚡ Sou o teu tutor de {disciplina_escolhida}. Que desafio vamos resolver hoje?"}]

    for msg in st.session_state[chave_memoria]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    mensagem_aluno = st.chat_input("Escreve a tua dúvida aqui...")

    if mensagem_aluno:
        with st.chat_message("user"):
            st.markdown(mensagem_aluno)
        st.session_state[chave_memoria].append({"role": "user", "content": mensagem_aluno})

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
            
            conteudo_para_ia = [prompt_secreto]
            
            mensagens_recentes = st.session_state[chave_memoria][-8:]
            for m in mensagens_recentes:
                conteudo_para_ia.append(f"{m['role']}: {m['content']}")
            
            if imagem_pil:
                conteudo_para_ia.append(imagem_pil)
            
            conteudo_para_ia.append(f"Pergunta atual do aluno: {mensagem_aluno}")

            try:
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
            with st.spinner("O Watty está a desenhar os exercícios... 🛠️"):
                prompt_treino = f"""
                És o Watty, o tutor de elite para alunos em Portugal.
                Cria um teste rigoroso de 5 perguntas sobre: {tema_exercicios}.

                REGRAS OBRIGATÓRIAS (Lê com atenção!):
                1. FOCO NO PROGRAMA: Os exercícios têm de ser EXCLUSIVAMENTE focados na matéria de {disciplina_escolhida} do {ano_escolhido}.
                2. DIFICULDADE: Nível de Exame Nacional ou Teste Final para o {ano_escolhido}.
                3. DIVERSIDADE: Inclui 3 perguntas de Escolha Múltipla e 2 Perguntas Abertas.
                4. ALEATORIEDADE: A opção correta TEM de ser distribuída aleatoriamente (A, B, C ou D).
                
                🎨 REGRAS DE ESTÉTICA VISUAL (MUITO IMPORTANTE):
                É PROIBIDO colocar as opções de resposta na mesma linha. Tens de usar o formato de lista do Markdown (com um traço inicial) para que fiquem umas por baixo das outras.
                
                Usa EXATAMENTE este molde visual para as perguntas:

                ### 📝 Pergunta [Número]
                **[Texto detalhado da Pergunta]**

                - **A)** [Opção]
                - **B)** [Opção]
                - **C)** [Opção]
                - **D)** [Opção]

                ---

                Quando terminares as 5 perguntas, tens OBRIGATORIAMENTE de escrever a seguinte palavra-passe exata:
                ===SOLUCOES===
                
                Por baixo dessa palavra-passe, escreve a chave de correção:
                **Pergunta 1:** [Opção Correta] - [Explicação]
                """
                try:
                    resposta_treino = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_treino)
                    texto_completo = resposta_treino.text
                    
                    # O TRUQUE PARA ESCONDER AS SOLUÇÕES
                    if "===SOLUCOES===" in texto_completo:
                        # Cortamos o texto em dois pedaços usando a palavra-passe secreta
                        partes = texto_completo.split("===SOLUCOES===")
                        perguntas = partes[0]
                        solucoes = partes[1]
                        
                        # Mostramos as perguntas normalmente
                        st.markdown(perguntas)
                        
                        # Mostramos as soluções dentro de uma caixa expansível!
                        with st.expander("👀 Ver Chave de Correção e Explicações"):
                            st.markdown(solucoes)
                    else:
                        # Caso a IA se esqueça da palavra-passe (raro), mostra tudo normal
                        st.markdown(texto_completo)
                        
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



