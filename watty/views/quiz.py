"""Aba Quizzes: treino rápido e Boss Battle."""

import json

import streamlit as st
import streamlit.components.v1 as components

from watty.config import GEMINI_MODEL
from watty.prompts.exams import build_prompt_exame
from watty.prompts.quiz_prompts import prompt_correcao_resposta_aberta, prompt_quiz_misto
from watty.services.sheets import acao_jogo, guardar_no_excel
from watty.utils.charts import exibir_com_graficos


def render_quiz_tab(
    client,
    ano_escolhido: str,
    disciplina_escolhida: str,
    exemplo_atual: str,
) -> None:
    st.title(f"🏋️ Fábrica de Exercícios: {disciplina_escolhida}")

    tab_rapido, tab_boss = st.tabs(["⚡ Treino Rápido (5 Perguntas)", "⚔️ Boss Battle (Exame 100 min)"])

    # --- ABA 1: TREINO RÁPIDO (AGORA 100% INTERATIVO 🎮) ---
    with tab_rapido:
        st.markdown("Treino Rápido para aquecer! 🔥")

        col_input, col_btn = st.columns([3, 1])
        with col_input:
            tema_exercicios = st.text_input(f"O que queres treinar? (Ex: {exemplo_atual})", key="input_rapido")
        with col_btn:
            st.write(""); st.write("")
            btn_gerar = st.button("Gerar Nível ⚙️", use_container_width=True)

        if btn_gerar and tema_exercicios:
            with st.spinner("O Watty está a forjar o teu nível... 🛠️"):
                prompt_treino = prompt_quiz_misto(
                    tema_exercicios, ano_escolhido, disciplina_escolhida
                )
                try:
                    resposta = client.models.generate_content(
                        model=GEMINI_MODEL, contents=prompt_treino
                    )
                    texto_limpo = (
                        resposta.text.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    quiz_data = json.loads(texto_limpo)
                    st.session_state.quiz_atual = quiz_data
                    st.session_state.quiz_idx = 0
                    st.session_state.quiz_acertos = 0
                    st.session_state.quiz_pontos = 0
                    st.session_state.quiz_pontos_max = sum(
                        q.get("pontos", 10) for q in quiz_data
                    )
                    st.session_state.quiz_respondido = False
                    st.session_state.hint_usado = False
                    st.session_state.correcao_aberta = None
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Erro ao gerar exercícios. (Erro: {e})")

    # --- QUIZ MISTO UMA PERGUNTA DE CADA VEZ ---
    if "quiz_atual" in st.session_state and st.session_state.quiz_atual:
        quiz = st.session_state.quiz_atual
        idx = st.session_state.quiz_idx
        total = len(quiz)

        if idx >= total:
            # --- ECRÃ FINAL ---
            pontos = st.session_state.quiz_pontos
            pontos_max = st.session_state.quiz_pontos_max
            nota = round((pontos / pontos_max) * 20, 1) if pontos_max > 0 else 0
        
            st.markdown("---")
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("📊 Nota Final", f"{nota}/20")
            col_r2.metric("🏆 Pontos", f"{pontos}/{pontos_max}")
            col_r3.metric("⭐ Classificação", 
                "Excelente!" if nota >= 18 else 
                "Muito Bom!" if nota >= 16 else 
                "Bom!" if nota >= 14 else 
                "Suficiente" if nota >= 10 else "Insuficiente")
        
            xp_ganho = int((pontos / pontos_max) * 100) if pontos_max > 0 else 0
            if xp_ganho > 0:
                acao_jogo(ganho_xp=xp_ganho, motivo=f"Quiz misto ({nota}/20)")
                st.balloons()
        
            if st.button("🔄 Novo treino", type="primary", use_container_width=True):
                for k in ["quiz_atual","quiz_idx","quiz_acertos","quiz_pontos",
                          "quiz_pontos_max","quiz_respondido","hint_usado","correcao_aberta"]:
                    st.session_state.pop(k, None)
                st.rerun()

        else:
            q = quiz[idx]
            tipo = q.get("tipo", "multipla_escolha")
            pontos_pergunta = q.get("pontos", 10)

            # Barra de progresso
            st.progress(idx / total)
        
            # Badge do tipo de pergunta
            badge_map = {
                "multipla_escolha": ("🔵 Escolha Múltipla", f"+{pontos_pergunta} pts"),
                "resposta_curta":   ("✏️ Resposta Curta",   f"+{pontos_pergunta} pts"),
                "desenvolvimento":  ("📝 Desenvolvimento",  f"+{pontos_pergunta} pts"),
                "calculo":          ("🔢 Cálculo",          f"+{pontos_pergunta} pts"),
                "ensaio":           ("📖 Ensaio",           f"+{pontos_pergunta} pts"),
            }
            badge_label, badge_pts = badge_map.get(tipo, ("❓", ""))
            st.markdown(f"**Pergunta {idx+1} de {total}** &nbsp; `{badge_label}` &nbsp; `{badge_pts}`", unsafe_allow_html=True)
            st.markdown(f"### {q['pergunta']}")

            # --- HINT ---
            if not st.session_state.get("quiz_respondido", False):
                if not st.session_state.get("hint_usado", False):
                    if st.button("💡 Ver dica (-5 XP)"):
                        st.session_state.hint_usado = True
                        st.session_state.xp = max(0, st.session_state.xp - 5)
                        st.rerun()
                else:
                    st.warning(f"💡 **Dica:** {q['dica']}")

            # =============================================
            # TIPO 1: ESCOLHA MÚLTIPLA
            # =============================================
            if tipo == "multipla_escolha":
                if not st.session_state.get("quiz_respondido", False):
                    for opcao in q['opcoes']:
                        if st.button(opcao, key=f"opt_{idx}_{opcao}", use_container_width=True):
                            st.session_state[f"resp_{idx}"] = opcao
                            st.session_state.quiz_respondido = True
                            # Calcular pontos imediatamente
                            if opcao == q['resposta_correta']:
                                pts = pontos_pergunta - (5 if st.session_state.get("hint_usado") else 0)
                                st.session_state.quiz_pontos += max(0, pts)
                            st.rerun()
                else:
                    resposta_dada = st.session_state.get(f"resp_{idx}")
                    for opcao in q['opcoes']:
                        if opcao == q['resposta_correta']:
                            st.success(f"✅ {opcao}")
                        elif opcao == resposta_dada:
                            st.error(f"❌ {opcao}")
                        else:
                            st.button(opcao, key=f"dis_{idx}_{opcao}", disabled=True, use_container_width=True)
                
                    if resposta_dada == q['resposta_correta']:
                        pts = pontos_pergunta - (5 if st.session_state.get("hint_usado") else 0)
                        st.success(f"🎉 Correto! **+{max(0,pts)} pontos**")
                    else:
                        st.error(f"❌ Errado. A correta era: **{q['resposta_correta']}**")
                
                    st.info(f"💡 **Watty diz:** {q['explicacao']}")

            # =============================================
            # TIPO 2: RESPOSTA ABERTA (curta, desenvolvimento, cálculo, ensaio)
            # =============================================
            else:
                altura_map = {"resposta_curta": 80, "desenvolvimento": 160, "calculo": 160, "ensaio": 280}
                placeholder_map = {
                    "resposta_curta":  "Escreve a tua resposta em 1 a 3 linhas...",
                    "desenvolvimento": "Escreve um parágrafo completo com os conceitos-chave...",
                    "calculo":         "Apresenta todos os passos do cálculo (dados → fórmula → resolução → resposta)...",
                    "ensaio":          "Desenvolve o teu texto de opinião com introdução, argumentos e conclusão...",
                }

                if not st.session_state.get("quiz_respondido", False):
                    resposta_aluno = st.text_area(
                        "A tua resposta:",
                        height=altura_map.get(tipo, 120),
                        placeholder=placeholder_map.get(tipo, "Escreve aqui..."),
                        key=f"open_{idx}"
                    )
                
                    col_sub1, col_sub2 = st.columns([2,1])
                    with col_sub1:
                        btn_submeter = st.button("✅ Submeter resposta", type="primary", use_container_width=True)
                    with col_sub2:
                        btn_skip = st.button("⏭️ Saltar (0 pts)", use_container_width=True)
                
                    if btn_skip:
                        st.session_state[f"resp_{idx}"] = ""
                        st.session_state.correcao_aberta = {
                            "nota": 0, 
                            "feedback": "Pergunta saltada.", 
                            "resposta_modelo": q.get("resposta_modelo","")
                        }
                        st.session_state.quiz_respondido = True
                        st.rerun()
                
                    if btn_submeter:
                        if not resposta_aluno or len(resposta_aluno.strip()) < 5:
                            st.warning("Escreve uma resposta antes de submeter!")
                        else:
                            with st.spinner("🧠 O Watty está a corrigir a tua resposta..."):
                                prompt_correcao = prompt_correcao_resposta_aberta(
                                    disciplina_escolhida,
                                    ano_escolhido,
                                    q,
                                    resposta_aluno,
                                    pontos_pergunta,
                                )
                                try:
                                    resp_correcao = client.models.generate_content(
                                        model=GEMINI_MODEL, contents=prompt_correcao
                                    )
                                    texto_correcao = resp_correcao.text.replace("```json","").replace("```","").strip()
                                    correcao = json.loads(texto_correcao)
                                
                                    st.session_state[f"resp_{idx}"] = resposta_aluno
                                    st.session_state.quiz_pontos += correcao.get("nota", 0)
                                    st.session_state.correcao_aberta = correcao
                                    st.session_state.quiz_respondido = True
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro na correção: {e}")

                else:
                    # Mostrar a resposta do aluno e a correção
                    correcao = st.session_state.get("correcao_aberta", {})
                    nota_obtida = correcao.get("nota", 0)
                    percentagem = (nota_obtida / pontos_pergunta * 100) if pontos_pergunta > 0 else 0
                
                    st.markdown("**A tua resposta:**")
                    st.markdown(f"> {st.session_state.get(f'resp_{idx}', '') or '_Saltada_'}")
                
                    if percentagem >= 70:
                        st.success(f"**Nota: {nota_obtida}/{pontos_pergunta} pontos** ({percentagem:.0f}%) ✅")
                    elif percentagem >= 40:
                        st.warning(f"**Nota: {nota_obtida}/{pontos_pergunta} pontos** ({percentagem:.0f}%) ⚠️")
                    else:
                        st.error(f"**Nota: {nota_obtida}/{pontos_pergunta} pontos** ({percentagem:.0f}%) ❌")
                
                    st.info(f"💬 **Feedback do Watty:** {correcao.get('feedback','')}")
                
                    with st.expander("📖 Ver resposta modelo"):
                        st.markdown(correcao.get("resposta_modelo", q.get("resposta_modelo", "")))

            # --- BOTÃO PRÓXIMA (comum a todos os tipos) ---
            if st.session_state.get("quiz_respondido", False):
                st.markdown("---")
                if st.button("Próxima pergunta →", type="primary", use_container_width=True):
                    st.session_state.quiz_idx += 1
                    st.session_state.quiz_respondido = False
                    st.session_state.hint_usado = False
                    st.session_state.correcao_aberta = None
                    st.rerun()

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
                        prompt_exame = build_prompt_exame(
                            disciplina_escolhida, ano_escolhido, temas_exame
                        )
                        try:
                            resposta_exame = client.models.generate_content(
                                model=GEMINI_MODEL, contents=prompt_exame
                            )
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
                        guardar_no_excel(
                            "Boss Battle",
                            st.session_state.temas_atuais,
                            "Exame Concluído",
                            ano_escolhido,
                            disciplina_escolhida,
                        )
                        st.session_state.exame_iniciado = False
                        st.session_state.conteudo_exame = ""
                        st.rerun()
            else:
                exibir_com_graficos(st.session_state.conteudo_exame)
                if st.button("Voltar atrás"):
                    st.session_state.exame_iniciado = False
                    st.rerun()
