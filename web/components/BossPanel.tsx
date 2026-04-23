"use client";

import { useState } from "react";
import { AssistantBody } from "./AssistantBody";
import { ExamTimer } from "./ExamTimer";
import { EXEMPLOS } from "@/lib/constants";
import { cicloExameGlobal } from "@/lib/prompts";
import type { SessionPayload } from "@/lib/types";

export function BossPanel({
  ano,
  disciplina,
  onSessionUpdate,
}: {
  ano: string;
  disciplina: string;
  onSessionUpdate: (s: SessionPayload) => void;
}) {
  const exemplo = EXEMPLOS[disciplina] ?? "Tema da matéria";
  const [modo, setModo] = useState<"temas" | "global">("temas");
  const [temasInput, setTemasInput] = useState("");
  const [iniciado, setIniciado] = useState(false);
  const [conteudo, setConteudo] = useState("");
  const [temasAtuais, setTemasAtuais] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const temasExame =
    modo === "global"
      ? `Todo o programa oficial das Aprendizagens Essenciais de ${disciplina} referente a todo o ciclo de exame (${cicloExameGlobal(disciplina, ano)}).`
      : temasInput.trim();

  const gerar = async () => {
    if (modo === "temas" && !temasInput.trim()) {
      setErr("Escreve os temas ou escolhe o Exame Global!");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const res = await fetch("/api/exam/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          disciplina,
          ano,
          temas: temasExame,
        }),
      });
      const data = (await res.json()) as { text?: string; error?: string };
      if (!res.ok) throw new Error(data.error || "Erro ao gerar exame");
      setConteudo(data.text ?? "");
      setTemasAtuais(temasExame);
      setIniciado(true);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  const concluir = async () => {
    try {
      await fetch("/api/logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          ano,
          disciplina,
          aba: "Boss Battle",
          tema: temasAtuais,
          resposta: "Exame Concluído",
        }),
      });
      const res = await fetch("/api/xp/award", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ gained: 500 }),
      });
      const data = (await res.json()) as { session?: SessionPayload; error?: string };
      if (!res.ok) throw new Error(data.error || "Erro XP");
      if (data.session) onSessionUpdate(data.session);
      setIniciado(false);
      setConteudo("");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    }
  };

  if (!iniciado) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-black text-[#4A148C]">⚔️ O Teste Final (Modelos IAVE 2025)</h2>
        <p className="text-[#311B52]">
          Mistura vários temas. O Watty vai gerar um Exame Simulado rigoroso com um relógio de 100 minutos.
        </p>
        <div className="space-y-2">
          <label className="flex items-center gap-2 font-semibold text-[#4A148C]">
            <input
              type="radio"
              checked={modo === "temas"}
              onChange={() => setModo("temas")}
            />
            🎯 Temas específicos
          </label>
          <label className="flex items-center gap-2 font-semibold text-[#4A148C]">
            <input
              type="radio"
              checked={modo === "global"}
              onChange={() => setModo("global")}
            />
            🌍 Exame global (Simulacro IAVE)
          </label>
        </div>
        {modo === "temas" ? (
          <input
            className="watty-input w-full"
            placeholder={`Temas (ex.: ${exemplo})`}
            value={temasInput}
            onChange={(e) => setTemasInput(e.target.value)}
          />
        ) : (
          <div className="rounded-xl border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
            🚨 Prepara-te! Este modo vai testar TODA a matéria do ciclo (
            {cicloExameGlobal(disciplina, ano)}).
          </div>
        )}
        <button type="button" className="watty-btn w-full" disabled={busy} onClick={() => void gerar()}>
          🚀 Gerar exame e iniciar relógio
        </button>
        {err && <p className="text-sm text-red-700">{err}</p>}
      </div>
    );
  }

  const temSolucoes = conteudo.includes("===SOLUCOES===");
  const [parteEx, parteSol] = temSolucoes
    ? conteudo.split("===SOLUCOES===")
    : [conteudo, ""];

  return (
    <div className="space-y-4">
      <ExamTimer />
      <p className="rounded-xl bg-white/90 p-3 text-sm font-semibold text-[#311B52]">
        <strong>Temas em teste:</strong> {temasAtuais}
      </p>
      <div className="rounded-2xl border-2 border-[#D1C4E9] bg-white/90 p-4">
        <AssistantBody text={(temSolucoes ? parteEx : conteudo).trim()} />
      </div>
      {temSolucoes && (
        <>
          <hr className="border-[#D1C4E9]" />
          <details className="rounded-xl border-2 border-[#9C27B0] bg-[#F3E5F5] p-4">
            <summary className="cursor-pointer font-black text-[#4A148C]">
              👀 Entregar exame e ver correção
            </summary>
            <div className="mt-4">
              <AssistantBody text={parteSol.trim()} />
            </div>
          </details>
          <button type="button" className="watty-btn w-full" onClick={() => void concluir()}>
            🏁 Concluir e voltar ao menu (+500 XP)
          </button>
        </>
      )}
      <button
        type="button"
        className="watty-btn-outline w-full text-sm"
        onClick={() => {
          setIniciado(false);
          setConteudo("");
        }}
      >
        Voltar atrás
      </button>
      {err && <p className="text-sm text-red-700">{err}</p>}
    </div>
  );
}
