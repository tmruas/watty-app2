"""Constantes da app (sem segredos)."""

# Google Sheets / Drive
SPREADSHEET_NAME = "Watty_Logs"
WORKSHEET_PERFIS = "Perfis"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Gemini
GEMINI_MODEL = "gemini-2.5-flash"

LISTA_ANOS = ["8º Ano", "9º Ano", "10º Ano", "11º Ano", "12º Ano"]

DISCIPLINAS_BAS = [
    "Matemática",
    "Português",
    "Físico-Química",
    "Ciências Naturais",
    "História",
    "Geografia",
    "Inglês",
]

DISCIPLINAS_SEC = [
    "Matemática A",
    "Matemática B",
    "MACS",
    "Português",
    "Economia",
    "Físico-Química",
    "Filosofia",
    "Biologia e Geologia",
    "História A",
    "Geometria Descritiva",
    "Inglês",
]

EXEMPLOS_POR_DISCIPLINA = {
    "Matemática": "Teorema de Pitágoras, Equações",
    "Matemática A": "Limites, Trigonometria",
    "Físico-Química": "Leis de Newton, Tabela Periódica",
    "Economia": "Inflação, Lei de Engel",
    "Português": "Os Lusíadas, Fernando Pessoa",
    "História": "Revolução Francesa",
    "Biologia e Geologia": "Mitose, ADN",
}


def disciplinas_para_ano(ano_escolhido: str) -> list[str]:
    if ano_escolhido in ("8º Ano", "9º Ano"):
        return DISCIPLINAS_BAS
    return DISCIPLINAS_SEC


def exemplo_para_disciplina(disciplina: str) -> str:
    return EXEMPLOS_POR_DISCIPLINA.get(disciplina, "Tema da matéria")
