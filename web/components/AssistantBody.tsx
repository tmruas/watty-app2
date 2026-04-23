"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { parseChartCsv, splitGraficoParts } from "@/lib/grafico";

function ChartBlock({ csv }: { csv: string }) {
  const rows = parseChartCsv(csv);
  if (!rows) {
    return (
      <p className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
        Não foi possível desenhar o gráfico a partir dos dados da IA.
      </p>
    );
  }
  const chartData = rows.map((r) => ({ label: r.name, ...r.values }));
  const keys = Object.keys(rows[0]?.values ?? {});

  return (
    <div className="h-72 w-full min-w-0 rounded-xl border-2 border-[#D1C4E9] bg-white p-2 shadow-sm">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E1BEE7" />
          <XAxis dataKey="label" tick={{ fill: "#4A148C", fontSize: 12 }} />
          <YAxis tick={{ fill: "#4A148C", fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {keys.map((k, i) => (
            <Line
              key={k}
              type="monotone"
              dataKey={k}
              stroke={["#9C27B0", "#7B1FA2", "#FFC107", "#4A148C"][i % 4]}
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AssistantBody({ text }: { text: string }) {
  const parts = splitGraficoParts(text);
  return (
    <div className="space-y-4">
      {parts.map((p, i) =>
        p.type === "text" ? (
          <div
            key={i}
            className="max-w-none text-[#311B52] [&_h1]:text-2xl [&_h1]:font-black [&_h1]:text-[#4A148C] [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-[#4A148C] [&_h3]:font-bold [&_h3]:text-[#4A148C] [&_a]:text-[#7B1FA2] [&_a]:underline [&_ul]:my-2 [&_ol]:my-2 [&_li]:my-1 [&_p]:my-2"
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{p.value}</ReactMarkdown>
          </div>
        ) : (
          <ChartBlock key={i} csv={p.csv} />
        ),
      )}
    </div>
  );
}
