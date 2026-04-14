import datetime

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

from watty.config import SCOPES, SPREADSHEET_NAME, WORKSHEET_PERFIS


def _credentials():
    return Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )


def _cliente_gspread():
    return gspread.authorize(_credentials())


def carregar_perfil(nome_aluno):
    try:
        cliente = _cliente_gspread()
        aba_perfis = cliente.open(SPREADSHEET_NAME).worksheet(WORKSHEET_PERFIS)

        registos = aba_perfis.get_all_records()
        hoje = datetime.date.today()

        for i, linha in enumerate(registos):
            if str(linha["Nome"]).strip().lower() == nome_aluno.strip().lower():
                ultimo_login_str = str(linha["Ultimo_Login"])
                streak_atual = int(linha["Streak"])

                try:
                    ultimo_login_data = datetime.datetime.strptime(
                        ultimo_login_str, "%d/%m/%Y"
                    ).date()
                    diferenca_dias = (hoje - ultimo_login_data).days

                    if diferenca_dias == 1:
                        streak_atual += 1
                    elif diferenca_dias > 1:
                        streak_atual = 1
                except Exception:
                    streak_atual = 1

                aba_perfis.update_cell(i + 2, 5, hoje.strftime("%d/%m/%Y"))
                aba_perfis.update_cell(i + 2, 4, streak_atual)

                return (
                    int(linha["XP"]),
                    int(linha["Nivel"]),
                    streak_atual,
                    i + 2,
                )

        aba_perfis.append_row(
            [nome_aluno, 0, 1, 1, hoje.strftime("%d/%m/%Y")]
        )
        num_linhas = len(aba_perfis.get_all_values())
        return 0, 1, 1, num_linhas

    except Exception as e:
        print(f"Erro na BD: {e}")
        return 0, 1, 1, 2


def guardar_no_excel(aba, tema_pergunta, resposta_ia, ano_escolhido, disciplina_escolhida):
    try:
        cliente = _cliente_gspread()
        folha = cliente.open(SPREADSHEET_NAME).sheet1

        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nome = st.session_state.get("nome_aluno", "Desconhecido")

        folha.append_row(
            [
                agora,
                nome,
                ano_escolhido,
                disciplina_escolhida,
                aba,
                tema_pergunta,
                resposta_ia,
            ]
        )

    except Exception as e:
        print(f"Erro ao gravar no Google Sheets: {e}")


def acao_jogo(ganho_xp, motivo):
    st.session_state.xp += ganho_xp

    novo_nivel = (st.session_state.xp // 200) + 1
    if novo_nivel > st.session_state.nivel:
        st.session_state.nivel = novo_nivel
        st.toast(f"🎉 SUBISTE PARA O NÍVEL {novo_nivel}!", icon="🔥")
        st.balloons()

    st.toast(f"+{ganho_xp} XP ({motivo})", icon="🎮")

    try:
        aba_perfis = _cliente_gspread().open(SPREADSHEET_NAME).worksheet(WORKSHEET_PERFIS)
        aba_perfis.update_cell(st.session_state.linha_bd, 2, st.session_state.xp)
        aba_perfis.update_cell(st.session_state.linha_bd, 3, st.session_state.nivel)
    except Exception:
        pass
