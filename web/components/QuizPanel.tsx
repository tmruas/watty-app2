"use client";

import { useCallback, useState } from "react";
import type { QuizQuestion, SessionPayload } from "@/lib/types";
import { EXEMPLOS } from "@/lib/constants";

const BADGE: Record<string, [string, string]> = {
  multipla_escolha: ["🔵 Escolha Múltipla", "pts"],
  resposta_curta: ["✏️ Resposta Curta", "pts"],
  desenvolvimento: ["📝 Desenvolvimento", "pts"],
  calculo: ["🔢 Cálculo", "pts"],
  ensaio: ["📖 Ensaio", "pts"],
};

export function QuizPanel({
  session: _session,
  ano,
  disciplina,
  onSessionUpdate,
}: {
  session: SessionPayload;
  ano: string;
  disciplina: string;
  onSessionUpdate: (s: SessionPayload) => void;
}) {
  void _session;
  const exemplo = EXEMPLOS[disciplina] ?? "Tema da matéria";
  const [tema, setTema] = useState("");
  const [quiz, setQuiz] = useState<QuizQuestion[] | null>(null);
  const [idx, setIdx] = useState(0);
  const [pontos, setPontos] = useState(0);
  const [pontosMax, setPontosMax] = useState(0);
  const [respondido, setRespondido] = useState(false);
  const [hintUsado, setHintUsado] = useState(false);
  const [correcao, setCorrecao] = useState<{
    nota: number;
    feedback: string;
    resposta_modelo?: string;
  } | null>(null);
  const [respAberta, setRespAberta] = useState("");
  const [respEscolha, setRespEscolha] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [xpRegistado, setXpRegistado] = useState(false);

  const resetQuiz = () => {
    setQuiz(null);
    setIdx(0);
    setPontos(0);
    setPontosMax(0);
    setRespondido(false);
    setHintUsado(false);
    setCorrecao(null);
    setRespAberta("");
    setRespEscolha(null);
    setErr(null);
    setXpRegistado(false);
  };

  const awardXp = useCallback(
    async (gained: number) => {
      const res = await fetch("/api/xp/award", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ gained }),
      });
      const data = (await res.json()) as {
        session?: SessionPayload;
        levelUp?: boolean;
        error?: string;
      };
      if (!res.ok) throw new Error(data.error || "Erro XP");
      if (data.session) onSessionUpdate(data.session);
      return data.levelUp;
    },
    [onSessionUpdate],
  );

  const gerar = async () => {
    if (!tema.trim()) return;
    setBusy(true);
    setErr(null);
    try {
      const res = await fetch("/api/quiz/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ tema, ano, disciplina }),
      });
      const data = (await res.json()) as { quiz?: QuizQuestion[]; error?: string };
      if (!res.ok) throw new Error(data.error || "Erro");
      const arr = Array.isArray(data.quiz) ? data.quiz : [];
      if (!arr.length) throw new Error("Quiz vazio");
      setQuiz(arr);
      setIdx(0);
      setPontos(0);
      setPontosMax(arr.reduce((s, q) => s + (q.pontos ?? 10), 0));
      setRespondido(false);
      setHintUsado(false);
      setCorrecao(null);
      setRespAberta("");
      setRespEscolha(null);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  const aplicarDica = async () => {
    setBusy(true);
    try {
      const res = await fetch("/api/xp/adjust", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ delta: -5 }),
      });
      const data = (await res.json()) as { session?: SessionPayload; error?: string };
      if (!res.ok) throw new Error(data.error || "Erro");
      if (data.session) onSessionUpdate(data.session);
      setHintUsado(true);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  const notaFinal =
    pontosMax > 0 ? Math.round((pontos / pontosMax) * 200) / 10 : 0;

  if (!quiz) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-black text-[#4A148C] md:text-3xl">
          🏋️ Fábrica de Exercícios: {disciplina}
        </h1>
        <p className="font-medium text-[#311B52]">Treino rápido para aquecer! 🔥</p>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <input
            className="watty-input flex-1"
            placeholder={`O que queres treinar? (Ex: ${exemplo})`}
            value={tema}
            onChange={(e) => setTema(e.target.value)}
          />
          <button type="button" className="watty-btn" disabled={busy} onClick={() => void gerar()}>
            Gerar Nível ⚙️
          </button>
        </div>
        {err && <p className="text-sm text-red-700">{err}</p>}
      </div>
    );
  }

  const total = quiz.length;
  if (idx >= total) {
    const xpGanho =
      pontosMax > 0 ? Math.floor((pontos / pontosMax) * 100) : 0;
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-black text-[#4A148C]">🏁 Resultado</h1>
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="watty-metric">
            <div className="text-xs font-extrabold uppercase text-[#7B1FA2]">📊 Nota final</div>
            <div className="text-2xl font-black text-[#4A148C]">{notaFinal}/20</div>
          </div>
          <div className="watty-metric">
            <div className="text-xs font-extrabold uppercase text-[#7B1FA2]">🏆 Pontos</div>
            <div className="text-2xl font-black text-[#4A148C]">
              {pontos}/{pontosMax}
            </div>
          </div>
          <div className="watty-metric">
            <div className="text-xs font-extrabold uppercase text-[#7B1FA2]">⭐ Classificação</div>
            <div className="text-lg font-black text-[#4A148C]">
              {notaFinal >= 18
                ? "Excelente!"
                : notaFinal >= 16
                  ? "Muito Bom!"
                  : notaFinal >= 14
                    ? "Bom!"
                    : notaFinal >= 10
                      ? "Suficiente"
                      : "Insuficiente"}
            </div>
          </div>
        </div>
        <button
          type="button"
          className="watty-btn w-full"
          onClick={() => {
            void (async () => {
              try {
                if (!xpRegistado && xpGanho > 0) {
                  await awardXp(xpGanho);
                  setXpRegistado(true);
                }
              } catch (e) {
                setErr(e instanceof Error ? e.message : "Erro ao gravar XP");
                return;
              }
              resetQuiz();
            })();
          }}
        >
          🔄 Novo treino
          {xpGanho > 0 && !xpRegistado ? ` (+${xpGanho} XP)` : ""}
        </button>
        {err && <p className="text-sm text-red-700">{err}</p>}
      </div>
    );
  }

  const q = quiz[idx];
  const tipo = q.tipo || "multipla_escolha";
  const ptsQ = q.pontos ?? 10;
  const [badgeLabel] = BADGE[tipo] ?? ["❓", ""];

  const submeterAberta = async () => {
    if (respAberta.trim().length < 5) {
      setErr("Escreve uma resposta antes de submeter!");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const res = await fetch("/api/quiz/grade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          disciplina,
          ano,
          pergunta: q.pergunta,
          resposta_modelo: q.resposta_modelo,
          criterios: q.criterios,
          pontos: ptsQ,
          respostaAluno: respAberta,
        }),
      });
      const data = (await res.json()) as {
        correcao?: { nota?: number; feedback?: string; resposta_modelo?: string };
        error?: string;
      };
      if (!res.ok) throw new Error(data.error || "Erro");
      const c = data.correcao ?? {};
      const nota = Math.max(0, Math.min(ptsQ, Number(c.nota) || 0));
      setPontos((p) => p + nota);
      setCorrecao({
        nota,
        feedback: c.feedback ?? "",
        resposta_modelo: c.resposta_modelo,
      });
      setRespondido(true);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#4A148C]">
        🏋️ Pergunta {idx + 1} de {total}
      </h1>
      <div className="h-2 w-full overflow-hidden rounded-full bg-[#D1C4E9]">
        <div
          className="h-full bg-[#9C27B0] transition-all"
          style={{ width: `${(idx / Math.max(1, total)) * 100}%` }}
        />
      </div>
      <p className="text-sm font-bold text-[#4A148C]">
        {badgeLabel} · +{ptsQ} pts
      </p>
      <h2 className="text-xl font-bold text-[#311B52]">{q.pergunta}</h2>

      {!respondido && !hintUsado && (
        <button type="button" className="watty-btn-outline text-sm" disabled={busy} onClick={() => void aplicarDica()}>
          💡 Ver dica (-5 XP)
        </button>
      )}
      {hintUsado && q.dica && (
        <div className="rounded-xl border border-amber-300 bg-amber-50 p-3 text-sm text-amber-950">
          💡 <strong>Dica:</strong> {q.dica}
        </div>
      )}

      {tipo === "multipla_escolha" && q.opcoes && (
        <div className="space-y-2">
          {!respondido ? (
            q.opcoes.map((op) => (
              <button
                key={op}
                type="button"
                className="watty-btn w-full text-left text-base normal-case"
                onClick={() => {
                  setRespEscolha(op);
                  if (op === q.resposta_correta) {
                    const pts = ptsQ - (hintUsado ? 5 : 0);
                    setPontos((p) => p + Math.max(0, pts));
                  }
                  setRespondido(true);
                }}
              >
                {op}
              </button>
            ))
          ) : (
            <div className="space-y-2">
              {q.opcoes.map((op) => (
                <div
                  key={op}
                  className={`rounded-xl border-2 px-4 py-2 font-semibold ${
                    op === q.resposta_correta
                      ? "border-green-600 bg-green-50 text-green-900"
                      : op === respEscolha
                        ? "border-red-500 bg-red-50 text-red-900"
                        : "border-[#D1C4E9] bg-white text-[#311B52]"
                  }`}
                >
                  {op === q.resposta_correta ? "✅ " : op === respEscolha ? "❌ " : ""}
                  {op}
                </div>
              ))}
              {respEscolha === q.resposta_correta ? (
                <p className="text-green-800">🎉 Correto!</p>
              ) : (
                <p className="text-red-800">A correta era: {q.resposta_correta}</p>
              )}
              {q.explicacao && (
                <div className="rounded-xl bg-[#E3F2FD] p-3 text-sm text-[#311B52]">
                  💡 <strong>Watty diz:</strong> {q.explicacao}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {tipo !== "multipla_escolha" && (
        <div className="space-y-3">
          {!respondido ? (
            <>
              <textarea
                className="watty-input min-h-[120px] w-full resize-y"
                placeholder="A tua resposta…"
                value={respAberta}
                onChange={(e) => setRespAberta(e.target.value)}
              />
              <div className="flex flex-wrap gap-2">
                <button type="button" className="watty-btn" disabled={busy} onClick={() => void submeterAberta()}>
                  ✅ Submeter resposta
                </button>
                <button
                  type="button"
                  className="watty-btn-outline"
                  disabled={busy}
                  onClick={() => {
                    setCorrecao({
                      nota: 0,
                      feedback: "Pergunta saltada.",
                      resposta_modelo: q.resposta_modelo,
                    });
                    setRespondido(true);
                  }}
                >
                  ⏭️ Saltar (0 pts)
                </button>
              </div>
            </>
          ) : (
            <div className="space-y-2 rounded-xl border-2 border-[#D1C4E9] bg-white/90 p-4">
              <p className="font-bold text-[#4A148C]">A tua resposta</p>
              <blockquote className="border-l-4 border-[#9C27B0] pl-3 text-[#311B52]">
                {respAberta || <em>Saltada</em>}
              </blockquote>
              {correcao && (
                <>
                  <p className="font-bold text-[#4A148C]">
                    Nota: {correcao.nota}/{ptsQ}
                  </p>
                  <p className="text-[#311B52]">💬 {correcao.feedback}</p>
                  <details className="text-sm">
                    <summary className="cursor-pointer font-bold text-[#7B1FA2]">
                      📖 Ver resposta modelo
                    </summary>
                    <div className="mt-2 whitespace-pre-wrap text-[#311B52]">
                      {correcao.resposta_modelo ?? q.resposta_modelo}
                    </div>
                  </details>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {respondido && (
        <button
          type="button"
          className="watty-btn w-full"
          onClick={() => {
            setIdx((i) => i + 1);
            setRespondido(false);
            setHintUsado(false);
            setCorrecao(null);
            setRespAberta("");
            setRespEscolha(null);
          }}
        >
          Próxima pergunta →
        </button>
      )}
      {err && <p className="text-sm text-red-700">{err}</p>}
    </div>
  );
}
