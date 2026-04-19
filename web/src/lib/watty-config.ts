/** Constantes partilhadas (sem segredos) — espelho de watty/config.py */

export const SPREADSHEET_NAME = "Watty_Logs";
export const WORKSHEET_PERFIS = "Perfis";
export const SCOPES = [
  "https://www.googleapis.com/auth/spreadsheets",
  "https://www.googleapis.com/auth/drive",
];

export const GEMINI_MODEL = "gemini-2.5-flash";

export const FOOTER_URL_LINKEDIN =
  "https://www.linkedin.com/company/wattylearn/";
export const FOOTER_EMAIL_AJUDA = "wattyexplica@gmail.com";

export const LISTA_ANOS = [
  "8º Ano",
  "9º Ano",
  "10º Ano",
  "11º Ano",
  "12º Ano",
] as const;

export const DISCIPLINAS_BAS = [
  "Matemática",
  "Português",
  "Físico-Química",
  "Ciências Naturais",
  "História",
  "Geografia",
  "Inglês",
] as const;

export const DISCIPLINAS_SEC = [
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
] as const;

export const EXEMPLOS_POR_DISCIPLINA: Record<string, string> = {
  Matemática: "Teorema de Pitágoras, Equações",
  "Matemática A": "Limites, Trigonometria",
  "Físico-Química": "Leis de Newton, Tabela Periódica",
  Economia: "Inflação, Lei de Engel",
  Português: "Os Lusíadas, Fernando Pessoa",
  História: "Revolução Francesa",
  "Biologia e Geologia": "Mitose, ADN",
};

export function disciplinasParaAno(ano: string): readonly string[] {
  if (ano === "8º Ano" || ano === "9º Ano") return DISCIPLINAS_BAS;
  return DISCIPLINAS_SEC;
}

export function exemploParaDisciplina(disciplina: string): string {
  return EXEMPLOS_POR_DISCIPLINA[disciplina] ?? "Tema da matéria";
}
