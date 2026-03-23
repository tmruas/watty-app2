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

# 🏋️ ABA QUIZZES (COM BOSS BATTLE)
elif aba_escolhida == "🏋️ Treinar (Quizzes)":
    st.title(f"🏋️ Fábrica de Exercícios: {disciplina_escolhida}")
    
    # Duas sub-abas para separar o treino da Batalha
    tab_rapido, tab_boss = st.tabs(["⚡ Treino Rápido (5 Perguntas)", "⚔️ Boss Battle (Exame 100 min)"])

    # --- ABA 1: TREINO RÁPIDO ---
    with tab_rapido:
        st.markdown("### Treino Rápido para aquecer! 🔥")
        tema_exercicios = st.text_input(f"Qual é o tema que queres treinar? (Ex: {exemplo_atual})", key="input_rapido")
        
        if st.button("Gerar Exercícios ⚙️", key="btn_rapido"):
            if tema_exercicios:
                with st.spinner("O Watty está a desenhar os exercícios... 🛠️"):
                    prompt_treino = f"""
                    Cria um teste de 5 perguntas sobre: {tema_exercicios} para o {ano_escolhido} de {disciplina_escolhida}.
                    Inclui 3 de Escolha Múltipla e 2 Abertas. A resposta correta da escolha múltipla deve ser aleatoriamente distribuída, não coloques apenas as opções B e C como corretas.
                    
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

    # --- ABA 2: BOSS BATTLE (SIMULADOR DE EXAMES 2025) ---
    with tab_boss:
        st.markdown("### ⚔️ O Teste Final (Modelos IAVE 2025)")
        st.write("Mistura vários temas. O Watty vai gerar um Exame Simulado rigoroso com um relógio implacável de 100 minutos.")

        # 1. Memória do Estado do Exame
        if "exame_iniciado" not in st.session_state:
            st.session_state.exame_iniciado = False
        if "conteudo_exame" not in st.session_state:
            st.session_state.conteudo_exame = ""

        # 2. Modo Configuração
        if not st.session_state.exame_iniciado:
            tipo_exame = st.radio("Como queres configurar a tua Boss Battle?", 
                                  ["🎯 Temas Específicos", "🌍 Exame Global (Simulacro IAVE)"])
            
            if tipo_exame == "🎯 Temas Específicos":
                temas_exame = st.text_input(f"📚 Escreve os temas misturados (Ex: {exemplo_atual}):", key="input_boss")
            else:
                # 🟢 O CÉREBRO DOS CICLOS DE EXAME
                if disciplina_escolhida in ["Português", "Matemática A", "História A"]:
                    ciclo = "10º, 11º e 12º anos"
                elif ano_escolhido in ["8º Ano", "9º Ano"]:
                    ciclo = "todo o 3º Ciclo (7º, 8º e 9º anos)"
                else:
                    ciclo = "10º e 11º anos" # Disciplinas Bienais (Economia, FQA, BG, etc.)
                    
                temas_exame = f"Todo o programa oficial das Aprendizagens Essenciais de {disciplina_escolhida} referente a todo o ciclo de exame ({ciclo})."
                st.info(f"🚨 Prepara-te! Este modo vai testar TODA a matéria do ciclo ({ciclo}).")

            if st.button("🚀 GERAR EXAME E INICIAR RELÓGIO (Custa 2 ⚡)", use_container_width=True):
                if tipo_exame == "🌍 Exame Global (Simulacro IAVE)" or (tipo_exame == "🎯 Temas Específicos" and temas_exame):
                    with st.spinner("A forjar a Boss Battle com o formato oficial do IAVE... Isto vai ser épico ⚔️"):
                        
                        # 🟢 O CÉREBRO DAS ESTRUTURAS IAVE (2025)
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

        # 3. Modo Jogo (Exame a Decorrer)
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
                st.markdown(partes[0])
                
                st.markdown("---")
                with st.expander("👀 ENTREGAR EXAME E VER CORREÇÃO"):
                    st.markdown(partes[1])
                    
                    if st.button("🏁 CONCLUIR E VOLTAR AO MENU", type="primary"):
                        st.success("Batalha Concluída! Ganhaste +500 XP!")
                        st.balloons()
                        guardar_no_excel("Boss Battle", st.session_state.temas_atuais, "Exame Concluído")
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
                    
                    guardar_no_excel("Resumo", tema_resumo, resposta_resumo.text)
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.warning("Escreve um tema!")
