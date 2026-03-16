import streamlit as st
import os
from google import genai
from PIL import Image
import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components

# --- 1. A TUA CHAVE DE ACESSO ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
client = genai.Client()

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Watty | O teu Tutor Inteligente", page_icon="⚡", layout="centered")

# --- 3. A PORTA DE ENTRADA (IDENTIFICAÇÃO) ---
if "nome_aluno" not in st.session_state:
    st.title("⚡ Bem-vindo ao Watty!")
    st.markdown("O teu tutor inteligente 24/7. Antes de começarmos, diz-me quem és:")
    
    nome_input = st.text_input("Qual é o teu Nome e Turma? (Ex: João Silva - 8ºB)")
    
    if st.button("Entrar no Watty 🚀"):
        if nome_input.strip() != "":
            st.session_state["nome_aluno"] = nome_input
            st.rerun() # Recarrega a página para a versão completa
        else:
            st.warning("⚠️ Epa, não te esqueças de escrever o teu nome para eu saber quem és!")
            
    # O st.stop() bloqueia o resto do site até o aluno se identificar
    st.stop()

# --- 4. FUNÇÃO PARA GRAVAR NO GOOGLE SHEETS ---
def guardar_no_excel(aba, tema_pergunta, resposta_ia):
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credenciais = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        cliente = gspread.authorize(credenciais)
        
        # O NOME TEM DE ESTAR IGUAL AO QUE DESTE NO GOOGLE DRIVE!
        folha = cliente.open("Watty_Logs").sheet1
        
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nome = st.session_state.get("nome_aluno", "Desconhecido")
        
        folha.append_row([agora, nome, ano_escolhido, disciplina_escolhida, aba, tema_pergunta, resposta_ia])
        
    except Exception as e:
        # Mostra erro no terminal mas não "cracha" o site para o aluno
        print(f"Erro ao gravar no Google Sheets: {e}")

# --- 5. MENU LATERAL ---
st.sidebar.image("https://api.dicebear.com/7.x/bottts/svg?seed=Watty&backgroundColor=1CB0F6", width=100)
st.sidebar.title("⚡ Menu do Watty")
st.sidebar.success(f"👤 Olá, {st.session_state['nome_aluno']}!")

lista_anos = ["8º Ano", "9º Ano", "10º Ano", "11º Ano", "12º Ano"]
ano_escolhido = st.sidebar.selectbox("🎓 Escolhe o Ano:", lista_anos)

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

disciplina_escolhida = st.sidebar.selectbox("📚 Escolhe a Disciplina:", lista_disciplinas)

exemplos = {
    "Matemática": "Teorema de Pitágoras, Equações",
    "Matemática A": "Limites, Trigonometria",
    "Físico-Química": "Leis de Newton, Tabela Periódica",
    "Economia": "Inflação, Lei de Engel",
    "Português": "Os Lusíadas, Fernando Pessoa",
    "História": "Revolução Francesa",
    "Biologia e Geologia": "Mitose, ADN"
}
exemplo_atual = exemplos.get(disciplina_escolhida, "Tema da matéria")

st.sidebar.markdown("---")
aba_escolhida = st.sidebar.radio("O que queres fazer?", ["💬 Chat Socrático", "🏋️ Treinar (Quizzes)", "📚 Aprender (Resumos)"])

# --- 6. AS ABAS ---

# 💬 ABA CHAT
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
És o Watty, um tutor especialista em {disciplina_escolhida} para o {ano_escolhido} em Portugal.

⚠️ REGRAS DE OURO DE CONTEÚDO:
1. RIGOR PEDAGÓGICO: Foca-te EXCLUSIVAMENTE nos conteúdos das Aprendizagens Essenciais do Ministério da Educação para o {ano_escolhido}. 
2. EVITA O EXCESSO: Se um aluno perguntar algo que é de nível universitário ou de outro ano (ex: Curvas de Engel detalhadas vs Lei de Engel básica), explica apenas o que é necessário para o 10º ano. Diz algo como: "Para o teu nível, o que precisas de saber é..."
3. LINGUAGEM: Usa termos técnicos que aparecem nos manuais portugueses (ex: usar 'Unidade de Consumo' em vez de termos brasileiros ou demasiado técnicos).
4. MÉTODO SOCRÁTICO: Nunca dês a resposta de bandeja. Guia o aluno com perguntas.
5. VISÃO: Se houver imagem, ajuda a decifrar o enunciado passo a passo.
            """
            
            conteudo_para_ia = [prompt_secreto]
            
            mensagens_recentes = st.session_state[chave_memoria][-4:]
            for m in mensagens_recentes:
                conteudo_para_ia.append(f"{m['role']}: {m['content']}")
            
            if imagem_pil:
                conteudo_para_ia.append(imagem_pil)
            
            conteudo_para_ia.append(f"Pergunta do aluno: {mensagem_aluno}")

            try:
                resposta_ia = client.models.generate_content(model='gemini-2.5-flash', contents=conteudo_para_ia)
                st.markdown(resposta_ia.text)
                st.session_state[chave_memoria].append({"role": "assistant", "content": resposta_ia.text})
                
                # 🔴 O ROBÔ GRAVA O CHAT AQUI
                guardar_no_excel("Chat", mensagem_aluno, resposta_ia.text)
                
            except Exception as e:
                st.error(f"Erro na IA: {e}")

# 🏋️ ABA QUIZZES
# 🏋️ ABA QUIZZES
elif aba_escolhida == "🏋️ Treinar (Quizzes)":
    st.title(f"🏋️ Fábrica de Exercícios: {disciplina_escolhida}")
    
    # CRIAMOS DUAS ABAS DENTRO DO TREINO PARA SEPARAR AS ÁGUAS!
    tab_rapido, tab_boss = st.tabs(["⚡ Treino Rápido (5 Perguntas)", "⚔️ Boss Battle (Exame 100 min)"])

    # -----------------------------------------
    # ABA 1: O TEU CÓDIGO ORIGINAL (Treino Rápido)
    # -----------------------------------------
    with tab_rapido:
        st.markdown("### Treino Rápido para aquecer! 🔥")
        tema_exercicios = st.text_input(f"Qual é o tema que queres treinar? (Ex: {exemplo_atual})", key="input_rapido")
        
        if st.button("Gerar Exercícios ⚙️", key="btn_rapido"):
            if tema_exercicios:
                with st.spinner("O Watty está a desenhar os exercícios... 🛠️"):
                    prompt_treino = f"""
                    Cria um teste de 5 perguntas sobre: {tema_exercicios} para o {ano_escolhido} de {disciplina_escolhida}.
                    Inclui 3 de Escolha Múltipla (as respostas têm de ser distribuidas aleatoriamente, não incluir apenas B e C) e 2 Abertas.
                    
                    Usa EXATAMENTE este molde:
                    ### 📝 Pergunta [Número]
                    **[Texto da Pergunta]**
                    - **A)** [Opção]
                    - **B)** [Opção]
                    - **C)** [Opção]
                    - **D)** [Opção]
                    ---
                    
                    No fim escreve a palavra-passe ===SOLUCOES=== e por baixo a chave de correção.
                    """
                    try:
                        resposta_treino = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_treino)
                        texto_completo = resposta_treino.text.replace("🔸", "\n\n🔸").replace("\n---", "\n\n---\n")

                        if "===SOLUCOES===" in texto_completo:
                            partes = texto_completo.split("===SOLUCOES===")
                            st.markdown(partes[0])
                            with st.expander("👀 Ver Chave de Correção e Explicações"):
                                st.markdown(partes[1])
                        else:
                            st.markdown(texto_completo)
                            
                        guardar_no_excel("Quiz Rápido", tema_exercicios, texto_completo)
                            
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                st.warning("Escreve um tema!")

    # -----------------------------------------
    # ABA 2: A NOVA BOSS BATTLE (Exame Simulado)
    # -----------------------------------------
    with tab_boss:
        st.markdown("### ⚔️ O Teste Final")
        st.write("Mistura vários temas. O Watty vai gerar um Exame Simulado com um relógio implacável de 100 minutos.")

        # 1. Memória do Estado do Exame
        if "exame_iniciado" not in st.session_state:
            st.session_state.exame_iniciado = False
        if "conteudo_exame" not in st.session_state:
            st.session_state.conteudo_exame = ""

        # 2. Modo Configuração (Antes do Exame começar)
        if not st.session_state.exame_iniciado:
            temas_exame = st.text_input("📚 Escreve os temas misturados 
            
            if st.button("🚀 GERAR EXAME E INICIAR RELÓGIO", use_container_width=True):
                if temas_exame:
                    with st.spinner("A forjar a Boss Battle... Isto vai ser épico ⚔️"):
                        prompt_exame = f"""
                        Cria um EXAME SIMULADO de {disciplina_escolhida} para o {ano_escolhido}.
                        Temas a misturar: {temas_exame}.
                        Gera 20 perguntas no total (10 de Escolha Múltipla difíceis (as respostas têm de ser distribuidas aleatoriamente, não incluir apenas B e C) e 10 de Desenvolvimento (com cálculos e desenvolvimento).
                        
                        Usa EXATAMENTE este molde:
                        ### 📝 Pergunta [Número]
                        **[Texto da Pergunta]**
                        - **A)** [Opção]
                        - **B)** [Opção]
                        - **C)** [Opção]
                        - **D)** [Opção]
                        ---
                        
                        No fim escreve a palavra-passe ===SOLUCOES=== e por baixo a chave de correção super detalhada.
                        """
                        try:
                            resposta_exame = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_exame)
                            texto_exame = resposta_exame.text.replace("🔸", "\n\n🔸").replace("\n---", "\n\n---\n")
                            
                            # Grava na memória e arranca!
                            st.session_state.conteudo_exame = texto_exame
                            st.session_state.exame_iniciado = True
                            st.session_state.temas_atuais = temas_exame
                            st.rerun() # Atualiza o ecrã para mostrar o relógio
                        except Exception as e:
                            st.error(f"Erro ao gerar exame: {e}")
                else:
                    st.warning("Tens de escrever os temas para o exame!")

        # 3. Modo Jogo (Exame a Decorrer)
        else:
            # O Relógio Injetado em HTML (Fica vermelho e a contar para trás)
            components.html(
                """
                <div style="font-size: 30px; font-weight: bold; color: #FF4B4B; text-align: center; font-family: sans-serif; padding: 10px; border: 2px solid #FF4B4B; border-radius: 10px; background-color: #ffeaea;">
                    ⏱️ Tempo Restante: <span id="timer">100:00</span>
                </div>
                <script>
                    let time = 100 * 60;
                    setInterval(function() {
                        let minutes = Math.floor(time / 60);
                        let seconds = time % 60;
                        document.getElementById("timer").innerHTML = minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
                        if(time > 0) time--;
                    }, 1000);
                </script>
                """, height=80
            )
            
            st.info(f"**Temas em teste:** {st.session_state.temas_atuais}")
            
            # Mostra o exame
            if "===SOLUCOES===" in st.session_state.conteudo_exame:
                partes = st.session_state.conteudo_exame.split("===SOLUCOES===")
                st.markdown(partes[0])
                
                st.markdown("---")
                # Apenas quando o aluno entrega é que vê as soluções
                with st.expander("👀 ENTREGAR EXAME E VER CORREÇÃO"):
                    st.markdown(partes[1])
                    
                    if st.button("🏁 CONCLUIR E VOLTAR AO MENU", type="primary"):
                        st.success("Ganhaste +500 XP!")
                        st.balloons()
                        # Regista a vitória no Excel
                        guardar_no_excel("Boss Battle", st.session_state.temas_atuais, "Exame Concluído")
                        # Faz reset à memória para poder jogar outro dia
                        st.session_state.exame_iniciado = False
                        st.session_state.conteudo_exame = ""
                        st.rerun()
            else:
                st.markdown(st.session_state.conteudo_exame)
                if st.button("Voltar atrás"):
                    st.session_state.exame_iniciado = False
                    st.rerun()
# 📚 ABA RESUMOS
elif aba_escolhida == "📚 Aprender (Resumos)":
    st.title(f"📚 Máquina de Resumos: {disciplina_escolhida}")
    
    tema_resumo = st.text_input(f"O que precisas de resumir? (Ex: {exemplo_atual})")
    
    if st.button("Criar Resumo Mágico 🪄"):
        if tema_resumo:
            with st.spinner("A processar resumo... 📚"):
                prompt_resumo = f"""
                Cria um resumo sobre {tema_resumo} focado no programa de {disciplina_escolhida} do {ano_escolhido}.
                Divide em: 1. O Conceito Central, 2. A Anatomia da Matéria, 3. Exemplo Prático, 4. Exceções, 5. Dica Ninja.
                """
                try:
                    resposta_resumo = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_resumo)
                    st.markdown(resposta_resumo.text)
                    
                    # 🔴 O ROBÔ GRAVA O RESUMO AQUI
                    guardar_no_excel("Resumo", tema_resumo, resposta_resumo.text)
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("Escreve um tema!")








