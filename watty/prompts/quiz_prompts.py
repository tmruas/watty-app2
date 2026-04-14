"""Prompts para geração e correção de quizzes."""


def prompt_quiz_misto(tema_exercicios: str, ano_escolhido: str, disciplina_escolhida: str) -> str:
    return f"""
                Cria um quiz misto de 6 perguntas sobre: {tema_exercicios} para o {ano_escolhido} de {disciplina_escolhida}.

            Distribui assim:
            - 3 perguntas de Escolha Múltipla (tipo "multipla_escolha")
            - 1 pergunta de Resposta Curta (tipo "resposta_curta") — 1 a 3 linhas
            - 1 pergunta de Desenvolvimento (tipo "desenvolvimento") — 1 parágrafo
            - 1 pergunta de Cálculo OU Ensaio, consoante a disciplina (tipo "calculo" ou "ensaio")

            OBRIGATÓRIO: Devolve APENAS um array JSON válido. Sem markdown, sem texto antes ou depois.
            Usa EXATAMENTE esta estrutura para cada tipo:

            Para escolha múltipla:
            {{
              "tipo": "multipla_escolha",
              "pergunta": "Texto da pergunta",
              "opcoes": ["Opção A", "Opção B", "Opção C", "Opção D"],
              "resposta_correta": "Opção A",
              "dica": "Dica sem revelar a resposta.",
              "explicacao": "Explicação curta.",
              "pontos": 10
            }}

            Para resposta curta, desenvolvimento, cálculo ou ensaio:
            {{
              "tipo": "resposta_curta",
              "pergunta": "Texto da pergunta",
              "dica": "Dica orientadora.",
              "resposta_modelo": "Resposta completa e ideal que o aluno deveria dar.",
              "criterios": "Critérios de correção: o que é obrigatório mencionar.",
              "pontos": 20
            }}

            O campo "tipo" pode ser: multipla_escolha, resposta_curta, desenvolvimento, calculo, ensaio.
            As respostas corretas das escolhas múltiplas devem ser aleatórias (A, B, C ou D com igual probabilidade).
            """


def prompt_correcao_resposta_aberta(
    disciplina_escolhida: str,
    ano_escolhido: str,
    q: dict,
    resposta_aluno: str,
    pontos_pergunta: int,
) -> str:
    return f"""
                                És o Watty, um professor rigoroso mas justo de {disciplina_escolhida} ({ano_escolhido}).

                                PERGUNTA: {q['pergunta']}
                                RESPOSTA MODELO: {q.get('resposta_modelo', '')}
                                CRITÉRIOS DE CORREÇÃO: {q.get('criterios', '')}
                                RESPOSTA DO ALUNO: {resposta_aluno}
                                PONTUAÇÃO MÁXIMA: {pontos_pergunta} pontos

                                Avalia a resposta do aluno e devolve APENAS um JSON com esta estrutura exata:
                                {{
                                  "nota": <número entre 0 e {pontos_pergunta}>,
                                  "feedback": "<feedback construtivo em 2-3 frases: o que estava certo, o que faltou, como melhorar>",
                                  "resposta_modelo": "<resposta modelo completa e ideal>"
                                }}
                                Sem markdown, sem texto antes ou depois. Apenas o JSON.
                                """
