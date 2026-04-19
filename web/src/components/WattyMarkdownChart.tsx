"use client";

import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function parseCsvChart(block: string): { labelKey: string; data: Record<string, string | number>[] } | null {
  const lines = block
    .trim()
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);
  if (lines.length < 2) return null;
  const header = lines[0].split(",").map((c) => c.trim());
  if (header.length < 2) return null;
  const labelKey = header[0];
  const rows: Record<string, string | number>[] = [];
  for (let i = 1; i < lines.length; i++) {
    const cells = lines[i].split(",").map((c) => c.trim());
    if (cells.length < 2) continue;
    const row: Record<string, string | number> = { [labelKey]: cells[0] };
    for (let j = 1; j < header.length; j++) {
      const key = header[j];
      const raw = cells[j] ?? "";
      const n = parseFloat(raw.replace(",", "."));
      row[key] = Number.isFinite(n) ? n : raw;
    }
    rows.push(row);
  }
  if (!rows.length) return null;
  return { labelKey, data: rows };
}

function ChartBlock({ csv }: { csv: string }) {
  const parsed = useMemo(() => parseCsvChart(csv), [csv]);
  if (!parsed) {
    return (
      <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
        Não foi possível desenhar o gráfico a partir dos dados devolvidos pela IA.
      </p>
    );
  }
  const { labelKey, data } = parsed;
  const keys = Object.keys(data[0] ?? {}).filter((k) => k !== labelKey);
  const color = "#9C27B0";

  return (
    <div className="my-4 h-64 w-full max-w-3xl rounded-xl border border-watty-border bg-white p-2 shadow-sm">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E6DDF5" />
          <XAxis dataKey={labelKey} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          {keys.map((k) => (
            <Line
              key={k}
              type="monotone"
              dataKey={k}
              stroke={color}
              strokeWidth={2}
              dot={{ r: 3 }}
              name={k}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function WattyMarkdownChart({ text }: { text: string }) {
  const segments = useMemo(() => {
    const parts: { type: "md" | "chart"; value: string }[] = [];
    const re = /\[GRAFICO\]([\s\S]*?)\[\/GRAFICO\]/g;
    let last = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) {
        parts.push({ type: "md", value: text.slice(last, m.index) });
      }
      parts.push({ type: "chart", value: m[1] ?? "" });
      last = m.index + m[0].length;
    }
    if (last < text.length) {
      parts.push({ type: "md", value: text.slice(last) });
    }
    if (!parts.length) parts.push({ type: "md", value: text });
    return parts;
  }, [text]);

  return (
    <div className="max-w-none space-y-4 text-base leading-relaxed text-slate-800 [&_h1]:text-2xl [&_h1]:font-bold [&_h2]:mt-4 [&_h2]:text-xl [&_h2]:font-semibold [&_li]:my-1 [&_p]:my-2 [&_ul]:list-disc [&_ul]:pl-6">
      {segments.map((seg, i) =>
        seg.type === "chart" ? (
          <ChartBlock key={`c-${i}`} csv={seg.value} />
        ) : (
          <ReactMarkdown key={`m-${i}`} remarkPlugins={[remarkGfm]}>
            {seg.value}
          </ReactMarkdown>
        )
      )}
    </div>
  );
}
