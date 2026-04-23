/** Estruturas oficiais IAVE (2025) por disciplina — espelho do Streamlit. */
export const IAAVE_STRUCTURES: Record<string, string> = {
  Economia: `
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
                            `,
  "Matemática A": `
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
                            `,
  "Matemática B": `
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
                            `,
  MACS: `
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
                            `,
  Português: `
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
                            `,
  "Biologia e Geologia": `
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
                            `,
  "Físico-Química": `
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
                            `,
  "História A": `
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
                            `,
  Geografia: `
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
                            `,
  Filosofia: `
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
                            `,
  "Geometria Descritiva": `
                            O exame tem um total de 5 itens práticos de desenho (2 obrigatórios + 3 opcionais):
                            - Fornece as coordenadas rigorosas (abcissa, afastamento, cota) para 5 problemas (ex: intersecção de planos, sombras, perspetivas).
                            - O aluno desenha no papel e depois verifica as soluções geradas passo a passo pela IA.
                            `,
  Inglês: `
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
                            `,
};

export const IAAVE_DEFAULT = `
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
                        `;
