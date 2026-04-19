/** Metadados dos jogos HTML — espelho de watty/views/jogos.py */

export const ALLOWED_GAME_FILES = new Set([
  "jogo ADM8 modulo 7.html",
  "jogo ADM9.html",
  "jogo.html",
  "jogo_conserta_o_tempo.html",
  "jogo_fa_nr_1.html",
  "jogo_facto_fake.html",
  "jogo_filosofia.html",
  "jogo_geografia.html",
  "jogo_macs_1.html",
  "mercado_jogo (1).html",
]);

export type GameRow = {
  filename: string;
  title: string;
  cover: string;
};

export const GAMES_ROWS: GameRow[] = [
  {
    filename: "jogo ADM8 modulo 7.html",
    title: "Economia Módulo 7: O Grande Governo (Simulador)",
    cover: "linear-gradient(135deg,#1e3a5f 0%,#f1c40f 55%,#2c3e50 100%)",
  },
  {
    filename: "jogo ADM9.html",
    title: "Módulo 2: O Lobo de Wall Street (Mecanismos de Mercado)",
    cover: "linear-gradient(135deg,#0f2027 0%,#f1c40f 50%,#203a43 100%)",
  },
  {
    filename: "jogo.html",
    title: "EcoGov: Global Edition - Masterclass Economia",
    cover: "linear-gradient(135deg,#0f172a 0%,#3b82f6 45%,#1e293b 100%)",
  },
  {
    filename: "jogo_conserta_o_tempo.html",
    title: "WATTY - Conserta o Tempo (Definitivo)",
    cover: "linear-gradient(135deg,#9B5DE5 0%,#F15BB5 60%,#6D3AB5 100%)",
  },
  {
    filename: "jogo_fa_nr_1.html",
    title: "WATTY - Fã Nº 1",
    cover: "linear-gradient(135deg,#0D0814 0%,#9B5DE5 50%,#26183A 100%)",
  },
  {
    filename: "jogo_facto_fake.html",
    title: "WATTY - Facto ou Fake? (Mega Base de Dados)",
    cover: "linear-gradient(135deg,#F3EEFF 0%,#9B5DE5 40%,#6D3AB5 100%)",
  },
  {
    filename: "jogo_filosofia.html",
    title: "WATTY - Feed das Falácias",
    cover: "linear-gradient(135deg,#1A1025 0%,#E63946 45%,#9B5DE5 100%)",
  },
  {
    filename: "jogo_geografia.html",
    title: "WATTY - Geo-Alvo (Modo Exame)",
    cover: "linear-gradient(135deg,#0D0814 0%,#22c55e 40%,#9B5DE5 100%)",
  },
  {
    filename: "jogo_macs_1.html",
    title: "Afinador de Quotas - O Desafio dos 100 Níveis",
    cover: "linear-gradient(135deg,#F3EEFF 0%,#F15BB5 50%,#9B5DE5 100%)",
  },
  {
    filename: "mercado_jogo (1).html",
    title: "Watty | Ministro da Economia",
    cover: "linear-gradient(135deg,#0a0a12 0%,#a78bfa 45%,#f43f5e 100%)",
  },
];
