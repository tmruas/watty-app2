/** Nome curto para o HUD — perfis gravados como "Nome | idade | escola". */
export function nomeCurtoParaHud(nomeAluno: string): string {
  const parts = nomeAluno.split(" | ").map((s) => s.trim());
  if (parts.length >= 3) return parts[0] ?? nomeAluno;
  return nomeAluno;
}
