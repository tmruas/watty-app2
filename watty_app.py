import streamlit as st
import os
import json
from google import genai
from PIL import Image
import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
import pandas as pd
import io
import re

# --- 1. A TUA CHAVE DE ACESSO ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
client = genai.Client()

# --- 2. CONFIGURAÇÃO DA PÁGINA E ESTILO GAMIFICADO (UI/UX) ---
st.set_page_config(page_title="Watty | O teu Tutor Inteligente", page_icon="⚡", layout="wide")

# 🎨 A MAGIA DO CSS (Cores Oficiais Watty baseadas no Design)
st.markdown("""
    <style>
    /* 1. O Fundo Principal (Lavanda/Lilás Watty) */
    .stApp {
        background-color: #E6DDF5; 
    }
    
    /* Remove a barra superior cinzenta do Streamlit */
    .stApp > header {
        background-color: transparent;
    }

    /* 🚨 A CORREÇÃO DOS TELEMÓVEIS (Forçar texto a escuro) 🚨 */
    .stMarkdown p, .stMarkdown li, p, label, .stRadio label {
        color: #311B52 !important; /* Roxo muito escuro, quase preto, perfeito para ler */
        font-weight: 500;
    }

    /* 2. Menu Lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 3px solid #D1C4E9;
        box-shadow: 2px 0px 15px rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] * {
        color: #4A148C !important;
        font-weight: 600;
    }

    /* 3. Botões Principais (Chunky Roxo/Magenta) */
    div.stButton > button:first-child {
        background-color: #9C27B0 !important; 
        color: white !important; /* O botão continua a ter letras brancas! */
        font-weight: 900 !important;
        font-size: 18px !important;
        border-radius: 16px;
        border: 2px solid #7B1FA2;
        box-shadow: 0px 6px 0px #7B1FA2;
        padding: 10px 24px;
        transition: all 0.1s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:first-child:active {
        box-shadow: 0px 0px 0px #7B1FA2;
        transform: translateY(6px);
    }
    div.stButton > button:first-child:hover {
        background-color: #AB47BC !important;
    }

    /* 4. Caixas do HUD */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 2px solid #D1C4E9;
        border-radius: 16px;
        padding: 15px;
        border-bottom: 5px solid #FFC107; 
        box-shadow: 0 4px 10px rgba(156, 39, 176, 0.1);
        text-align: center;
    }
    
    div[data-testid="metric-container"] label {
        font-weight: 800;
        color: #7B1FA2 !important; 
        font-size: 14px;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-weight: 900;
        color: #4A148C !important; 
        font-size: 32px;
    }

    /* 5. Títulos Principais */
    h1, h2, h3 {
        color: #4A148C !important;
        font-weight: 900 !important;
        letter-spacing: -0.5px;
    }

    /* 6. Caixas de Texto (Inputs) */
    .stTextInput input, .stTextArea textarea {
        border-radius: 16px;
        border: 2px solid #D1C4E9;
        padding: 14px;
        font-size: 16px;
        font-weight: 600;
        background-color: #FFFFFF !important;
        color: #4A148C !important; /* Texto que o aluno escreve fica escuro */
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #FFC107;
        box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.3);
    }
    </style>
""", unsafe_allow_html=True)
# --- 3. A PORTA DE ENTRADA, GAMIFICAÇÃO E STREAKS ---
if "logado" not in st.session_state:
    st.session_state.logado = False

# Função para ler o Excel e calcular a Streak
def carregar_perfil(nome_aluno):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciais = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        cliente = gspread.authorize(credenciais)
        aba_perfis = cliente.open("Watty_Logs").worksheet("Perfis")
        
        registos = aba_perfis.get_all_records()
        hoje = datetime.date.today()
        
        # Procura o aluno na lista
        for i, linha in enumerate(registos):
            if str(linha["Nome"]).strip().lower() == nome_aluno.strip().lower():
                ultimo_login_str = str(linha["Ultimo_Login"])
                streak_atual = int(linha["Streak"])
                
                # Calcular se ele ganha Streak ou se a perdeu
                try:
                    ultimo_login_data = datetime.datetime.strptime(ultimo_login_str, "%d/%m/%Y").date()
                    diferenca_dias = (hoje - ultimo_login_data).days
                    
                    if diferenca_dias == 1:
                        streak_atual += 1 # Entrou no dia seguinte, a chama continua!
                    elif diferenca_dias > 1:
                        streak_atual = 1 # Falhou mais de um dia, a chama apagou :(
                except:
                    streak_atual = 1
                
                # Grava a data de hoje no Excel
                aba_perfis.update_cell(i + 2, 5, hoje.strftime("%d/%m/%Y"))
                aba_perfis.update_cell(i + 2, 4, streak_atual)
                
                return int(linha["XP"]), int(linha["Nivel"]), streak_atual, i + 2 # Retorna a linha para atualizar o XP depois
        
        # Se o aluno não existir, cria um novo guerreiro!
        aba_perfis.append_row([nome_aluno, 0, 1, 1, hoje.strftime("%d/%m/%Y")])
        num_linhas = len(aba_perfis.get_all_values())
        return 0, 1, 1, num_linhas
        
    except Exception as e:
        print(f"Erro na BD: {e}")
        return 0, 1, 1, 2 # Modo segurança caso o Excel falhe

if not st.session_state.logado:
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
    st.stop()

# --- FUNÇÃO DE GAMEPLAY (GANHAR XP E GRAVAR NO EXCEL) ---
def acao_jogo(ganho_xp, motivo):
    st.session_state.xp += ganho_xp
    
    # Subir de nível
    novo_nivel = (st.session_state.xp // 200) + 1
    if novo_nivel > st.session_state.nivel:
        st.session_state.nivel = novo_nivel
        st.toast(f"🎉 SUBISTE PARA O NÍVEL {novo_nivel}!", icon="🔥")
        st.balloons()
    
    st.toast(f"+{ganho_xp} XP ({motivo})", icon="🎮")
    
    # Grava no Excel silenciosamente em pano de fundo
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciais = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        cliente = gspread.authorize(credenciais)
        aba_perfis = cliente.open("Watty_Logs").worksheet("Perfis")
        aba_perfis.update_cell(st.session_state.linha_bd, 2, st.session_state.xp)
        aba_perfis.update_cell(st.session_state.linha_bd, 3, st.session_state.nivel)
    except:
        pass

# --- O NOVO HUD (COM A CHAMA DA STREAK 🔥) ---
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
# --- 4. FUNÇÕES ÚTEIS (EXCEL E GRÁFICOS) ---
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
        print(f"Erro ao gravar no Google Sheets: {e}")

def exibir_com_graficos(texto_ia):
    """Procura por dados de gráficos escondidos na resposta e desenha-os interativamente"""
    padrao = r'\[GRAFICO\](.*?)\[/GRAFICO\]'
    partes = re.split(padrao, texto_ia, flags=re.DOTALL)
    
    for i, parte in enumerate(partes):
        if i % 2 == 0:
            # Texto normal
            if parte.strip():
                st.markdown(parte)
        else:
            # Dados CSV gerados pela IA para fazer um gráfico
            try:
                dados_csv = parte.strip()
                df = pd.read_csv(io.StringIO(dados_csv))
                if len(df.columns) > 0:
                    df.set_index(df.columns[0], inplace=True)
                st.line_chart(df)
            except Exception as e:
                st.error("⚠️ [Erro ao processar o gráfico gerado pela IA]")

# A Regra de Ouro anti-alucinações para injetar nos prompts
REGRA_GRAFICOS = """
⚠️ REGRA PARA GRÁFICOS: NUNCA inventes ou uses links de imagens externas (como imgur). 
Se precisares de mostrar um gráfico de evolução, dados económicos, físicos ou matemáticos, fornece os dados num formato CSV simples, 
SEMPRE envolvidos entre as tags [GRAFICO] e [/GRAFICO].
Exemplo:
[GRAFICO]
Ano,Valor
2020,1.5
2021,4.0
2022,8.1
[/GRAFICO]
"""

# --- 5. MENU LATERAL ---
# Como o watty.jpeg está no teu GitHub/pasta, o Streamlit apanha-o logo!
try:
    st.sidebar.image("Design_sem_nome__3_-removebg-preview.png", use_container_width=True) 
except FileNotFoundError:
    st.sidebar.error("⚠️ Imagem 'Design_sem_nome__3_-removebg-preview.png' não encontrada. Verifica as maiúsculas e minúsculas!")

st.sidebar.title("⚡ Menu do Watty")
st.sidebar.success(f"👤 Olá, {st.session_state.get('nome_aluno', 'Pioneiro')}!")

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
        "Geometria Descritiva", "Inglês"
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

# --- 6. AS ABAS PRINCIPAIS ---

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
            if msg["role"] == "assistant":
                exibir_com_graficos(msg["content"])
            else:
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
2. EVITA O EXCESSO: Se um aluno perguntar algo que é de nível universitário ou de outro ano, explica apenas o que é necessário para o seu ano. Diz algo como: "Para o teu nível, o que precisas de saber é..."
3. LINGUAGEM: Usa termos técnicos que aparecem nos manuais portugueses.
4. MÉTODO SOCRÁTICO: Nunca dês a resposta de bandeja. Guia o aluno com perguntas.
5. VISÃO: Se houver imagem, ajuda a decifrar o enunciado passo a passo.
{REGRA_GRAFICOS}
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
                exibir_com_graficos(resposta_ia.text)
                st.session_state[chave_memoria].append({"role": "assistant", "content": resposta_ia.text})
                
                guardar_no_excel("Chat", mensagem_aluno, resposta_ia.text)
                
            except Exception as e:
                st.error(f"Erro na IA: {e}")

# 🏋️ ABA QUIZZES (COM BOSS BATTLE)
elif aba_escolhida == "🏋️ Treinar (Quizzes)":
    st.title(f"🏋️ Fábrica de Exercícios: {disciplina_escolhida}")
    
    tab_rapido, tab_boss = st.tabs(["⚡ Treino Rápido (5 Perguntas)", "⚔️ Boss Battle (Exame 100 min)"])

    # --- ABA 1: TREINO RÁPIDO (AGORA 100% INTERATIVO 🎮) ---
    with tab_rapido:
        st.markdown("### Treino Rápido para aquecer! 🔥")
        
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            tema_exercicios = st.text_input(f"O que queres treinar? (Ex: {exemplo_atual})", key="input_rapido")
        with col_btn:
            st.write("") # Espaço para alinhar
            st.write("")
            btn_gerar = st.button("Gerar Nível ⚙️", use_container_width=True)

        # 1. GERAR O QUIZ E GUARDAR NA MEMÓRIA
        if btn_gerar:
            if tema_exercicios:
                with st.spinner("O Watty está a forjar o teu nível... 🛠️"):
                    # O Prompt agora obriga a IA a falar em "Código JSON"
                    prompt_treino = f"""
                    Cria um teste de 5 perguntas de Escolha Múltipla sobre: {tema_exercicios} para o {ano_escolhido} de {disciplina_escolhida}.
                    OBRIGATÓRIO: Devolve APENAS um array JSON válido. Sem formatação markdown, sem texto antes ou depois.
                    Usa EXATAMENTE esta estrutura:
                    [
                      {{
                        "pergunta": "Texto da pergunta",
                        "opcoes": ["Opção A", "Opção B", "Opção C", "Opção D"],
                        "resposta_correta": "Opção A",
                        "explicacao": "Explicação curta do porquê."
                      }}
                    ]
                    A resposta correta tem de ser exatamente igual à string da opção. As opções corretas devem ser aleatórias.
                    """
                    try:
                        resposta_treino = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_treino)
                        
                        # Limpar a resposta da IA para garantir que é JSON puro
                        texto_limpo = resposta_treino.text.replace("```json", "").replace("```", "").strip()
                        import json
                        quiz_data = json.loads(texto_limpo)
                        
                        # Guardar o quiz na sessão para ele não desaparecer quando clicarmos!
                        st.session_state.quiz_atual = quiz_data
                        st.session_state.respostas_aluno = {} # Limpa respostas antigas
                        st.session_state.quiz_avaliado = False
                        st.rerun()
                            
                    except Exception as e:
                        st.error(f"⚠️ Erro ao gerar os exercícios. Tenta outro tema. (Erro interno: {e})")
            else:
                st.warning("Escreve um tema primeiro!")

        # 2. MOSTRAR O QUIZ INTERATIVO (Se houver um quiz na memória)
        if "quiz_atual" in st.session_state and st.session_state.quiz_atual:
            st.markdown("---")
            st.markdown(f"#### 🎯 Missão: {tema_exercicios}")
            
            # Desenhar as perguntas como Radio Buttons interativos
            for i, q in enumerate(st.session_state.quiz_atual):
                st.markdown(f"**{i+1}. {q['pergunta']}**")
                
                # Se já foi avaliado, bloqueia as opções (disabled=True)
                st.session_state.respostas_aluno[i] = st.radio(
                    "Escolhe a tua resposta:", 
                    q['opcoes'], 
                    key=f"q_{i}", 
                    disabled=st.session_state.get("quiz_avaliado", False),
                    label_visibility="collapsed"
                )
                st.markdown("<br>", unsafe_allow_html=True) # Espaçamento

            # 3. O BOTÃO DE AVALIAÇÃO (A Hora da Verdade)
            if not st.session_state.get("quiz_avaliado", False):
                if st.button("Verificar Respostas ✅", type="primary", use_container_width=True):
                    acertos = 0
                    
                    # Mostrar resultados visuais
                    for i, q in enumerate(st.session_state.quiz_atual):
                        resposta_dada = st.session_state.respostas_aluno[i]
                        if resposta_dada == q['resposta_correta']:
                            st.success(f"**Pergunta {i+1}:** ACERTASTE! 🎉")
                            acertos += 1
                        else:
                            st.error(f"**Pergunta {i+1}:** ERRASTE. ❌ A correta era: **{q['resposta_correta']}**")
                        
                        st.info(f"💡 **Watty diz:** {q['explicacao']}")
                    
                    # Dar o XP com base nos acertos (ex: 20 XP por cada resposta certa)
                    xp_ganho = acertos * 20
                    st.session_state.quiz_avaliado = True # Bloqueia o quiz para não repetir
                    
                    if acertos > 0:
                        acao_jogo(ganho_xp=xp_ganho, motivo=f"Quiz ({acertos}/5)")
                        st.balloons()
                    else:
                        st.toast("Não ganhaste XP. Tenta de novo!", icon="💔")
                        
                    st.button("Fazer outro treino 🔄", on_click=lambda: st.session_state.pop("quiz_atual"))

    # --- ABA 2: BOSS BATTLE (SIMULADOR DE EXAMES 2025) ---
    with tab_boss:
        st.markdown("### ⚔️ O Teste Final (Modelos IAVE 2025)")
        st.write("Mistura vários temas. O Watty vai gerar um Exame Simulado rigoroso com um relógio implacável de 100 minutos.")

        if "exame_iniciado" not in st.session_state:
            st.session_state.exame_iniciado = False
        if "conteudo_exame" not in st.session_state:
            st.session_state.conteudo_exame = ""

        if not st.session_state.exame_iniciado:
            tipo_exame = st.radio("Como queres configurar a tua Boss Battle?", 
                                  ["🎯 Temas Específicos", "🌍 Exame Global (Simulacro IAVE)"])
            
            if tipo_exame == "🎯 Temas Específicos":
                temas_exame = st.text_input(f"📚 Escreve os temas misturados (Ex: {exemplo_atual}):", key="input_boss")
            else:
                if disciplina_escolhida in ["Português", "Matemática A", "História A"]:
                    ciclo = "10º, 11º e 12º anos"
                elif ano_escolhido in ["8º Ano", "9º Ano"]:
                    ciclo = "todo o 3º Ciclo (7º, 8º e 9º anos)"
                else:
                    ciclo = "10º e 11º anos"
                    
                temas_exame = f"Todo o programa oficial das Aprendizagens Essenciais de {disciplina_escolhida} referente a todo o ciclo de exame ({ciclo})."
                st.info(f"🚨 Prepara-te! Este modo vai testar TODA a matéria do ciclo ({ciclo}).")

            if st.button("🚀 GERAR EXAME E INICIAR RELÓGIO (Custa 2 ⚡)", use_container_width=True):
                if tipo_exame == "🌍 Exame Global (Simulacro IAVE)" or (tipo_exame == "🎯 Temas Específicos" and temas_exame):
                    with st.spinner("A forjar a Boss Battle com o formato oficial do IAVE... Isto vai ser épico ⚔️"):
                        
                        # 🟢 O CÉREBRO DAS ESTRUTURAS IAVE (2025) ESTÁ DE VOLTA!
                        estruturas_iave = {
                            "Economia": """
                            O exame tem um total de 22 itens, focado na nova estrutura do IAVE (16 obrigatórios + 6 opcionais):
                            - PARTE 1 (Itens de Seleção): 15 perguntas de Escolha Múltipla.
                                    Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            - PARTE 2 (Itens de Construção): 7 perguntas de resposta restrita baseadas num texto, tabela ou gráfico de dados económicos.
                            - Nota: Indica no exame quais são as 4 perguntas opcionais de desenvolvimento.
                            """,
                            "Matemática A": """
                            O exame tem um total de 18 itens (12 obrigatórios + 6 opcionais):
                            - PARTE 1: 5 perguntas de Escolha Múltipla (teoria e raciocínio direto).
                                    Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            - PARTE 2: 13 problemas de desenvolvimento complexos (cálculos passo-a-passo, funções, geometria, probabilidades).
                            - Nota para a IA: Simula o modelo 2025, indicando que nos itens opcionais só contam as 3 melhores respostas.
                            """,
                            "Matemática B": """
                            O exame tem um total de 18 itens (12 obrigatórios + 6 opcionais):
                            - Foco em problemas práticos, otimização, grafos e estatística.
                            - Cerca de 5 Escolhas Múltiplas e 13 problemas de desenvolvimento contextualizados no quotidiano.
                                    Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            """,
                            "MACS": """
                            O exame tem um total de 14 itens (10 obrigatórios + 4 opcionais):
                            - Foco em métodos de votação, grafos, modelos financeiros e estatística.
                            - Cerca de 4 Escolhas Múltiplas e 10 problemas de desenvolvimento onde o aluno deve explicar o raciocínio.
                                    Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            """,
                            "Português": """
                            O exame tem um total de 15 itens (10 obrigatórios + 5 opcionais):
                            - GRUPO I (Educação Literária): Apresenta um excerto de uma obra. Gera 3 a 5 perguntas de interpretação.
                            - GRUPO II (Leitura e Gramática): Apresenta um texto não-literário. Gera 7 perguntas (escolha múltipla e resposta curta).
                                    Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            - GRUPO III (Produção Escrita): 1 proposta de redação de um texto de opinião (200-350 palavras) sobre um tema específico.
                            """,
                            "Biologia e Geologia": """
                            O exame tem um total de 28 itens (20 obrigatórios + 8 opcionais):
                            - A prova é composta por 4 Grupos (2 de Biologia, 2 de Geologia).
                            - Cada grupo DEVE começar com um texto descrevendo uma experiência, observação ou fenómeno.
                            - Após cada texto, gera várias perguntas de Escolha Múltipla e termina com 1 ou 2 perguntas de resposta restrita de relação de conceitos.
                                                                        Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            """,
                            "Físico-Química": """
                            O exame tem um total de 23 itens (15 obrigatórios + 8 opcionais):
                            - Divide-se em situações problemáticas de Física e de Química (contextos experimentais).
                            - Mistura Escolhas Múltiplas e problemas de cálculo rigoroso (obriga à apresentação de todas as fórmulas e unidades do S.I.).
                                                                        Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            """,
                            "História A": """
                            O exame tem um total de 14 itens (10 obrigatórios + 4 opcionais):
                            - GRUPO I e II: Apresenta textos históricos (fontes). Gera perguntas de escolha múltipla e respostas curtas baseadas na análise da fonte.
                                                                        Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            - GRUPO III: 1 ou 2 respostas extensas (desenvolvimento) exigindo a integração de conceitos, contextualização espacial e temporal.
                            """,
                            "Geografia": """
                            O exame tem um total de 28 itens (18 obrigatórios + 10 opcionais):
                            - Foco gigante em análise espacial.
                            - Descreve mapas, perfis topográficos ou gráficos e gera questões de Escolha Múltipla.
                            - Inclui perguntas de resposta restrita de análise crítica a problemas demográficos ou territoriais de Portugal.
                                                                                                        Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            """,
                            "Filosofia": """
                            O exame tem um total de 18 itens (12 obrigatórios + 6 opcionais):
                            - GRUPO I: 10 a 12 perguntas de Escolha Múltipla (lógica, ética, epistemologia).
                                                                                                        Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            - GRUPO II: Apresenta pequenos excertos de filósofos (Descartes, Hume, Kant, etc.). Pede a identificação de teses e argumentos.
                            - GRUPO III: 1 Ensaio Filosófico argumentativo onde o aluno deve justify uma posição.
                            """,
                            "Geometria Descritiva": """
                            O exame tem um total de 5 itens práticos de desenho (2 obrigatórios + 3 opcionais):
                            - Fornece as coordenadas rigorosas (abcissa, afastamento, cota) para 5 problemas (ex: intersecção de planos, sombras, perspetivas).
                            - O aluno desenha no papel e depois verifica as soluções geradas passo a passo pela IA.
                            """,
                            "Inglês": """
                            O exame testa a proficiência e compreensão:
                            - PART 1 (Reading): Apresenta um texto em inglês e faz 5 perguntas de Escolha Múltipla de interpretação.
                                                                                                        Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                            - PART 2 (Use of English): 5 frases para reescrever (sentence transformation) ou espaços para preencher com vocabulário/gramática.
                            - PART 3 (Writing): Pede um texto de opinião (essay) de 150-220 palavras em inglês sobre um tema atual.
                            """
                        }

                        estrutura_default = """
                        - GRUPO I: 10 perguntas de Escolha Múltipla.
                                                                                        Usa EXATAMENTE este molde:
                                    ### 📝 Pergunta [Número]
                                    **[Texto da Pergunta]**
                                    - **A)** [Opção]
                                    - **B)** [Opção]
                                    - **C)** [Opção]
                                    - **D)** [Opção]
                        - GRUPO II: 4 perguntas de resposta curta.
                        - GRUPO III: 1 pergunta de desenvolvimento longo.
                        """

                        estrutura_oficial = estruturas_iave.get(disciplina_escolhida, estrutura_default)

                        prompt_exame = f"""
                        Ages como o IAVE (Instituto de Avaliação Educativa) a criar o EXAME FINAL SIMULADO de {disciplina_escolhida} para o {ano_escolhido} em Portugal.
                        Temas a avaliar: {temas_exame}.

                        ⚠️ REGRAS DE OURO OBRIGATÓRIAS:
                        1. ALEATORIEDADE NA ESCOLHA MÚLTIPLA: A posição da resposta certa TEM DE SER ALEATÓRIA (A, B, C ou D). Proibido usar maioritariamente B ou C.
                        2. ESTRUTURA OFICIAL (MODELO 2025): Tens de respeitar EXATAMENTE a seguinte estrutura oficial do exame nacional desta disciplina:
                        
                        {estrutura_oficial}
                        
                        {REGRA_GRAFICOS}

                        ---
                        No fim do exame, escreve a palavra-passe ===SOLUCOES=== e por baixo gera a CHAVE DE CORREÇÃO SUPER DETALHADA.
                        Na correção das escolhas múltiplas, lista a grelha (ex: 1-A, 2-D...). Nos desenvolvimentos, indica os tópicos que o aluno deveria abordar (critérios de correção do IAVE).
                        """
                        try:
                            resposta_exame = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_exame)
                            texto_exame = resposta_exame.text.replace("🔸", "\n\n🔸").replace("\n---", "\n\n---\n")
                            
                            st.session_state.conteudo_exame = texto_exame
                            st.session_state.exame_iniciado = True
                            st.session_state.temas_atuais = temas_exame
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao gerar exame: {e}")
                else:
                    st.warning("Escreve os temas ou escolhe o Exame Global!")

        else:
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
            
            if "===SOLUCOES===" in st.session_state.conteudo_exame:
                partes = st.session_state.conteudo_exame.split("===SOLUCOES===")
                exibir_com_graficos(partes[0])
                
                st.markdown("---")
                with st.expander("👀 ENTREGAR EXAME E VER CORREÇÃO"):
                    exibir_com_graficos(partes[1])
                    
                    if st.button("🏁 CONCLUIR E VOLTAR AO MENU", type="primary"):
                        st.success("Batalha Concluída! Ganhaste +500 XP!")
                        st.balloons()
                        guardar_no_excel("Boss Battle", st.session_state.temas_atuais, "Exame Concluído")
                        st.session_state.exame_iniciado = False
                        st.session_state.conteudo_exame = ""
                        st.rerun()
            else:
                exibir_com_graficos(st.session_state.conteudo_exame)
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
                
                {REGRA_GRAFICOS}
                """
                try:
                    resposta_resumo = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_resumo)
                    exibir_com_graficos(resposta_resumo.text)
                    
                    guardar_no_excel("Resumo", tema_resumo, resposta_resumo.text)
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("Escreve um tema!")
