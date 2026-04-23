const GRAFICO_RE = /\[GRAFICO\]([\s\S]*?)\[\/GRAFICO\]/g;

export type GraficoPart =
  | { type: "text"; value: string }
  | { type: "chart"; csv: string };

export function splitGraficoParts(text: string): GraficoPart[] {
  const parts: GraficoPart[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  const re = new RegExp(GRAFICO_RE.source, GRAFICO_RE.flags);
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) {
      parts.push({ type: "text", value: text.slice(last, m.index) });
    }
    parts.push({ type: "chart", csv: (m[1] ?? "").trim() });
    last = m.index + m[0].length;
  }
  if (last < text.length) {
    parts.push({ type: "text", value: text.slice(last) });
  }
  if (parts.length === 0) {
    parts.push({ type: "text", value: text });
  }
  return parts;
}

export type ChartRow = { name: string; values: Record<string, number> };

/** Primeira coluna = eixo X; restantes = séries numéricas. */
export function parseChartCsv(csv: string): ChartRow[] | null {
  const lines = csv
    .trim()
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);
  if (lines.length < 2) return null;
  const header = lines[0].split(",").map((c) => c.trim());
  if (header.length < 2) return null;
  const seriesKeys = header.slice(1);
  const rows: ChartRow[] = [];
  for (let i = 1; i < lines.length; i++) {
    const cells = lines[i].split(",").map((c) => c.trim());
    if (cells.length < 2) continue;
    const name = cells[0];
    const values: Record<string, number> = {};
    for (let j = 0; j < seriesKeys.length; j++) {
      const n = parseFloat((cells[j + 1] ?? "").replace(",", "."));
      if (!Number.isNaN(n)) values[seriesKeys[j]] = n;
    }
    rows.push({ name, values });
  }
  return rows.length ? rows : null;
}
