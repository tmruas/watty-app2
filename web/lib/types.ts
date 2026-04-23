export type SessionPayload = {
  nome_aluno: string;
  linha_bd: number;
  xp: number;
  nivel: number;
  streak: number;
};

export type ChatMessage = { role: "user" | "assistant"; content: string };

export type QuizQuestion = {
  tipo: string;
  pergunta: string;
  opcoes?: string[];
  resposta_correta?: string;
  dica?: string;
  explicacao?: string;
  pontos?: number;
  resposta_modelo?: string;
  criterios?: string;
};
