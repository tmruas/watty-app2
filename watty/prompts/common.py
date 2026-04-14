"""Regras comuns injetadas nos prompts da IA."""

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
