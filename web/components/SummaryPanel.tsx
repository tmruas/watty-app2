"use client";

import { useState } from "react";
import { AssistantBody } from "./AssistantBody";
import { EXEMPLOS } from "@/lib/constants";

export function SummaryPanel({
  ano,
  disciplina,
}: {
  ano: string;
  disciplina: string;
}) {
  const exemplo = EXEMPLOS[disciplina] ?? "Tema da matéria";
  const [tema, setTema] = useState("");
  const [texto, setTexto] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const gerar = async () => {
    if (!tema.trim()) {
      setErr("Escreve um tema!");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const res = await fetch("/api/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ tema, disciplina, ano }),
      });
      const data = (await res.json()) as { text?: string; error?: string };
      if (!res.ok) throw new Error(data.error || "Erro");
      setTexto(data.text ?? "");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#4A148C] md:text-3xl">
        📚 Máquina de Resumos: {disciplina}
      </h1>
      <input
        className="watty-input w-full"
        placeholder={`O que precisas de resumir? (Ex: ${exemplo})`}
        value={tema}
        onChange={(e) => setTema(e.target.value)}
      />
      <button type="button" className="watty-btn" disabled={busy} onClick={() => void gerar()}>
        Criar Resumo Mágico 🪄
      </button>
      {err && <p className="text-sm text-red-700">{err}</p>}
      {texto && (
        <div className="rounded-2xl border-2 border-[#D1C4E9] bg-white/90 p-4">
          <AssistantBody text={texto} />
        </div>
      )}
    </div>
  );
}
