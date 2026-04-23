export const ANOS = ["8º Ano", "9º Ano", "10º Ano", "11º Ano", "12º Ano"] as const;

export const DISCIPLINAS_3_CICLO = [
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

export type Ano = (typeof ANOS)[number];
export type Disciplina =
  | (typeof DISCIPLINAS_3_CICLO)[number]
  | (typeof DISCIPLINAS_SEC)[number];

export function disciplinasParaAno(ano: string): readonly string[] {
  return ano === "8º Ano" || ano === "9º Ano"
    ? DISCIPLINAS_3_CICLO
    : DISCIPLINAS_SEC;
}

export const EXEMPLOS: Record<string, string> = {
  Matemática: "Teorema de Pitágoras, Equações",
  "Matemática A": "Limites, Trigonometria",
  "Matemática B": "Estatística, Grafos",
  MACS: "Métodos de votação, Finanças",
  "Físico-Química": "Leis de Newton, Tabela Periódica",
  Economia: "Inflação, Lei de Engel",
  Português: "Os Lusíadas, Fernando Pessoa",
  História: "Revolução Francesa",
  "História A": "Revolução Liberal",
  "Biologia e Geologia": "Mitose, ADN",
  Filosofia: "Ética, Epistemologia",
  "Geometria Descritiva": "Perspetivas, Sombras",
  "Ciências Naturais": "Célula, Ecossistemas",
  Geografia: "Clima, População",
  Inglês: "Reading, Writing",
};

export const MAIN_TABS = [
  { id: "chat", label: "💬 Chat Socrático" },
  { id: "quiz", label: "🏋️ Treinar (Quizzes)" },
  { id: "resumos", label: "📚 Aprender (Resumos)" },
  { id: "watty-tv", label: "📺 Watty TV" },
] as const;

export const SPREADSHEET_NAME = "Watty_Logs";
export const PERFIS_SHEET = "Perfis";
