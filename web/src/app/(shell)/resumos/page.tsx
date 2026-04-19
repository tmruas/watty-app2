"use client";

import { useState } from "react";
import { WattyMarkdownChart } from "@/components/WattyMarkdownChart";
import { useWattyUi } from "@/components/AppShell";
import { exemploParaDisciplina } from "@/lib/watty-config";

export default function ResumosPage() {
  const { ano, disciplina } = useWattyUi();
  const ex = exemploParaDisciplina(disciplina);
  const [tema, setTema] = useState("");
  const [out, setOut] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function gerar() {
    const t = tema.trim();
    if (!t) {
      setErr("Escreve um tema.");
      return;
    }
    setErr(null);
    setBusy(true);
    setOut(null);
    try {
      const res = await fetch("/api/ai/resumo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ ano, disciplina, tema: t }),
      });
      const data = (await res.json()) as { text?: string; error?: string };
      if (!res.ok) throw new Error(data.error ?? "Erro");
      setOut(data.text ?? "");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-black text-watty-purple">
        Máquina de resumos — {disciplina}
      </h1>
      <input
        className="w-full rounded-xl border-2 border-watty-border px-3 py-2 font-semibold text-watty-purple"
        placeholder={`O que precisas de resumir? (ex.: ${ex})`}
        value={tema}
        onChange={(e) => setTema(e.target.value)}
      />
      <button
        type="button"
        disabled={busy}
        onClick={() => void gerar()}
        className="rounded-xl bg-watty-btn px-6 py-2 font-black text-white shadow-watty disabled:opacity-50"
      >
        {busy ? "A processar…" : "Criar resumo mágico"}
      </button>
      {err && <p className="text-sm font-bold text-red-600">{err}</p>}
      {out && (
        <div className="rounded-2xl border border-watty-border bg-white/95 p-4">
          <WattyMarkdownChart text={out} />
        </div>
      )}
    </div>
  );
}
