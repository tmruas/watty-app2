"use client";

import { useCallback, useEffect, useState } from "react";
import { WattyMarkdownChart } from "@/components/WattyMarkdownChart";
import { useWattyUi } from "@/components/AppShell";
import { useWattyProfile } from "@/context/WattyProfileContext";
import { exemploParaDisciplina } from "@/lib/watty-config";

type QuizQ = Record<string, unknown> & {
  tipo?: string;
  pergunta?: string;
  opcoes?: string[];
  resposta_correta?: string;
  dica?: string;
  explicacao?: string;
  pontos?: number;
  resposta_modelo?: string;
  criterios?: string;
};

function BossTimer() {
  const [sec, setSec] = useState(100 * 60);
  useEffect(() => {
    const id = window.setInterval(() => {
      setSec((s) => (s > 0 ? s - 1 : 0));
    }, 1000);
    return () => window.clearInterval(id);
  }, []);
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return (
    <div className="rounded-lg border-2 border-red-400 bg-red-50 px-3 py-2 text-center text-lg font-bold text-red-700">
      Tempo restante: {m}:{s < 10 ? "0" : ""}
      {s}
    </div>
  );
}

export default function QuizPage() {
  const { ano, disciplina } = useWattyUi();
  const { profile, setLocalXpNivel, refresh } = useWattyProfile();
  const ex = exemploParaDisciplina(disciplina);

  const [tab, setTab] = useState<"rapido" | "boss">("rapido");
  const [temaRapido, setTemaRapido] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [quizAtual, setQuizAtual] = useState<QuizQ[] | null>(null);
  const [quizIdx, setQuizIdx] = useState(0);
  const [quizPontos, setQuizPontos] = useState(0);
  const [quizPontosMax, setQuizPontosMax] = useState(0);
  const [quizRespondido, setQuizRespondido] = useState(false);
  const [hintUsado, setHintUsado] = useState(false);
  const [respIdx, setRespIdx] = useState<string>("");
  const [openText, setOpenText] = useState("");
  const [correcaoAberta, setCorrecaoAberta] = useState<Record<
    string,
    unknown
  > | null>(null);

  const [bossIniciado, setBossIniciado] = useState(false);
  const [bossTipo, setBossTipo] = useState<"temas" | "global">("temas");
  const [bossTemasInput, setBossTemasInput] = useState("");
  const [bossConteudo, setBossConteudo] = useState("");
  const [bossTemasAtuais, setBossTemasAtuais] = useState("");

  const syncXpRemote = useCallback(
    async (xp: number, nivel: number) => {
      if (!profile) return;
      await fetch("/api/profile/xp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          xp,
          nivel,
          linha_bd: profile.linha_bd,
        }),
      });
    },
    [profile]
  );

  const gerarQuiz = async () => {
    const t = temaRapido.trim();
    if (!t) return;
    setErr(null);
    setBusy(true);
    try {
      const res = await fetch("/api/ai/quiz/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ ano, disciplina, tema: t }),
      });
      const data = (await res.json()) as { quiz?: QuizQ[]; error?: string };
      if (!res.ok) throw new Error(data.error ?? "Erro");
      const q = data.quiz ?? [];
      setQuizAtual(q);
      setQuizIdx(0);
      setQuizPontos(0);
      setQuizPontosMax(q.reduce((a, x) => a + (Number(x.pontos) || 10), 0));
      setQuizRespondido(false);
      setHintUsado(false);
      setRespIdx("");
      setOpenText("");
      setCorrecaoAberta(null);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  const q = quizAtual?.[quizIdx];
  const total = quizAtual?.length ?? 0;

  const aplicarXpGanho = async (ganho: number, motivo: string) => {
    if (!profile || ganho <= 0) return;
    const xp = profile.xp + ganho;
    const nivel = Math.floor(xp / 200) + 1;
    setLocalXpNivel(xp, nivel);
    await syncXpRemote(xp, nivel);
    void refresh();
    console.info(motivo);
  };

  const proximaPergunta = () => {
    setQuizIdx((i) => i + 1);
    setQuizRespondido(false);
    setHintUsado(false);
    setRespIdx("");
    setOpenText("");
    setCorrecaoAberta(null);
  };

  const resetTreino = () => {
    setQuizAtual(null);
    setQuizIdx(0);
    setQuizPontos(0);
    setQuizPontosMax(0);
  };

  const escolherOpcao = async (opcao: string) => {
    if (!q || quizRespondido) return;
    setRespIdx(opcao);
    setQuizRespondido(true);
    const pontosPergunta = Number(q.pontos) || 10;
    if (opcao === q.resposta_correta) {
      const pts = pontosPergunta - (hintUsado ? 5 : 0);
      setQuizPontos((p) => p + Math.max(0, pts));
    }
  };

  const usarDica = async () => {
    if (hintUsado || !profile) return;
    setHintUsado(true);
    const xp = Math.max(0, profile.xp - 5);
    const nivel = Math.floor(xp / 200) + 1;
    setLocalXpNivel(xp, nivel);
    await syncXpRemote(xp, nivel);
  };

  const submeterAberta = async () => {
    if (!q || quizRespondido) return;
    const t = openText.trim();
    if (t.length < 5) {
      setErr("Escreve uma resposta com pelo menos 5 caracteres.");
      return;
    }
    setErr(null);
    setBusy(true);
    try {
      const res = await fetch("/api/ai/quiz/grade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          ano,
          disciplina,
          question: q,
          resposta_aluno: t,
          pontos_pergunta: Number(q.pontos) || 20,
        }),
      });
      const data = (await res.json()) as {
        correcao?: { nota?: number };
        error?: string;
      };
      if (!res.ok) throw new Error(data.error ?? "Erro");
      const nota = Number(data.correcao?.nota ?? 0);
      setRespIdx(t);
      setCorrecaoAberta(data.correcao ?? {});
      setQuizPontos((p) => p + nota);
      setQuizRespondido(true);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  const saltarAberta = () => {
    if (!q) return;
    setCorrecaoAberta({
      nota: 0,
      feedback: "Pergunta saltada.",
      resposta_modelo: String(q.resposta_modelo ?? ""),
    });
    setRespIdx("");
    setQuizRespondido(true);
  };

  const gerarBoss = async () => {
    let temas = "";
    if (bossTipo === "temas") {
      temas = bossTemasInput.trim();
      if (!temas) {
        setErr("Indica os temas.");
        return;
      }
    } else {
      if (["Português", "Matemática A", "História A"].includes(disciplina)) {
        temas = `Todo o programa oficial das Aprendizagens Essenciais de ${disciplina} referente a todo o ciclo de exame (10º, 11º e 12º anos).`;
      } else if (ano === "8º Ano" || ano === "9º Ano") {
        temas = `Todo o programa oficial das Aprendizagens Essenciais de ${disciplina} referente a todo o ciclo de exame (7º, 8º e 9º anos).`;
      } else {
        temas = `Todo o programa oficial das Aprendizagens Essenciais de ${disciplina} referente a todo o ciclo de exame (10º e 11º anos).`;
      }
    }
    setErr(null);
    setBusy(true);
    try {
      const res = await fetch("/api/ai/exam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ ano, disciplina, temas }),
      });
      const data = (await res.json()) as { text?: string; error?: string };
      if (!res.ok) throw new Error(data.error ?? "Erro");
      setBossConteudo(data.text ?? "");
      setBossTemasAtuais(temas);
      setBossIniciado(true);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  const concluirBoss = async () => {
    if (!profile) return;
    await fetch("/api/logs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        aba: "Boss Battle",
        tema: bossTemasAtuais,
        resposta_ia: "Exame Concluído",
        ano,
        disciplina,
      }),
    });
    const xp = profile.xp + 500;
    const nivel = Math.floor(xp / 200) + 1;
    setLocalXpNivel(xp, nivel);
    await syncXpRemote(xp, nivel);
    setBossIniciado(false);
    setBossConteudo("");
    void refresh();
  };

  const notaFinal =
    quizPontosMax > 0 ? Math.round((quizPontos / quizPontosMax) * 200) / 10 : 0;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-black text-watty-purple">
        Fábrica de exercícios — {disciplina}
      </h1>

      <div className="flex gap-2 border-b border-watty-border pb-2">
        <button
          type="button"
          className={`rounded-lg px-4 py-2 text-sm font-bold ${
            tab === "rapido"
              ? "bg-watty-btn text-white"
              : "bg-white text-watty-purple"
          }`}
          onClick={() => setTab("rapido")}
        >
          Treino rápido
        </button>
        <button
          type="button"
          className={`rounded-lg px-4 py-2 text-sm font-bold ${
            tab === "boss"
              ? "bg-watty-btn text-white"
              : "bg-white text-watty-purple"
          }`}
          onClick={() => setTab("boss")}
        >
          Boss battle
        </button>
      </div>

      {err && <p className="text-sm font-bold text-red-600">{err}</p>}

      {tab === "rapido" && (
        <div className="space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              className="min-h-[48px] flex-1 rounded-xl border-2 border-watty-border px-3 font-semibold"
              placeholder={`O que queres treinar? (ex.: ${ex})`}
              value={temaRapido}
              onChange={(e) => setTemaRapido(e.target.value)}
            />
            <button
              type="button"
              disabled={busy}
              onClick={() => void gerarQuiz()}
              className="rounded-xl bg-watty-btn px-4 py-2 font-black text-white disabled:opacity-50"
            >
              Gerar nível
            </button>
          </div>

          {quizAtual && q && quizIdx < total && (
            <div className="space-y-4 rounded-2xl border border-watty-border bg-white/95 p-4">
              <div className="text-sm font-bold text-slate-600">
                Pergunta {quizIdx + 1} de {total}
              </div>
              <h2 className="text-lg font-bold text-watty-purple">
                {String(q.pergunta ?? "")}
              </h2>

              {!quizRespondido && !hintUsado && (
                <button
                  type="button"
                  className="text-sm font-bold text-amber-700 underline"
                  onClick={() => void usarDica()}
                >
                  Ver dica (−5 XP)
                </button>
              )}
              {hintUsado && (
                <p className="rounded-lg bg-amber-50 p-2 text-sm font-semibold text-amber-900">
                  Dica: {String(q.dica ?? "")}
                </p>
              )}

              {q.tipo === "multipla_escolha" && q.opcoes && (
                <div className="flex flex-col gap-2">
                  {q.opcoes.map((op) => (
                    <button
                      key={op}
                      type="button"
                      disabled={quizRespondido}
                      onClick={() => void escolherOpcao(op)}
                      className={`rounded-xl border-2 px-3 py-2 text-left font-semibold ${
                        quizRespondido
                          ? op === q.resposta_correta
                            ? "border-green-500 bg-green-50"
                            : op === respIdx
                              ? "border-red-400 bg-red-50"
                              : "border-slate-200 opacity-60"
                          : "border-watty-border hover:bg-watty-bg"
                      }`}
                    >
                      {op}
                    </button>
                  ))}
                </div>
              )}

              {q.tipo !== "multipla_escolha" && (
                <div className="space-y-2">
                  {!quizRespondido ? (
                    <>
                      <textarea
                        className="min-h-[120px] w-full rounded-xl border-2 border-watty-border p-2 font-medium"
                        value={openText}
                        onChange={(e) => setOpenText(e.target.value)}
                        placeholder="A tua resposta…"
                      />
                      <div className="flex gap-2">
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => void submeterAberta()}
                          className="rounded-xl bg-watty-btn px-4 py-2 font-bold text-white"
                        >
                          Submeter
                        </button>
                        <button
                          type="button"
                          onClick={saltarAberta}
                          className="rounded-xl border px-4 py-2 font-bold"
                        >
                          Saltar (0 pts)
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="space-y-2 text-sm">
                      <p className="font-bold">A tua resposta</p>
                      <blockquote className="border-l-4 border-watty-border pl-3">
                        {respIdx || "_Saltada_"}
                      </blockquote>
                      {correcaoAberta && (
                        <>
                          <p className="font-semibold text-watty-purple">
                            Nota: {String(correcaoAberta.nota ?? 0)} /{" "}
                            {String(q.pontos ?? 20)}
                          </p>
                          <p>{String(correcaoAberta.feedback ?? "")}</p>
                        </>
                      )}
                    </div>
                  )}
                </div>
              )}

              {quizRespondido && q.tipo === "multipla_escolha" && (
                <div className="text-sm">
                  {respIdx === q.resposta_correta ? (
                    <p className="font-bold text-green-700">Correto!</p>
                  ) : (
                    <p className="font-bold text-red-700">
                      Errado. Certa: {q.resposta_correta}
                    </p>
                  )}
                  <p className="mt-1 text-slate-700">{String(q.explicacao ?? "")}</p>
                </div>
              )}

              {quizRespondido && (
                <button
                  type="button"
                  onClick={proximaPergunta}
                  className="rounded-xl bg-watty-purple px-4 py-2 font-bold text-white"
                >
                  Próxima pergunta →
                </button>
              )}
            </div>
          )}

          {quizAtual && quizIdx >= total && (
            <div className="rounded-2xl border border-watty-border bg-white p-4 text-center">
              <p className="text-xl font-black text-watty-purple">
                Nota: {notaFinal}/20
              </p>
              <p className="mt-2 font-semibold">
                Pontos: {quizPontos}/{quizPontosMax}
              </p>
              <button
                type="button"
                className="mt-4 rounded-xl bg-watty-btn px-6 py-2 font-black text-white"
                onClick={() => {
                  const ganho =
                    quizPontosMax > 0
                      ? Math.round((quizPontos / quizPontosMax) * 100)
                      : 0;
                  void aplicarXpGanho(ganho, "Quiz");
                  resetTreino();
                }}
              >
                Novo treino
              </button>
            </div>
          )}
        </div>
      )}

      {tab === "boss" && (
        <div className="space-y-4">
          {!bossIniciado ? (
            <>
              <p className="text-sm text-slate-700">
                Simulador de exame (formato IAVE). Gera conteúdo longo — pode demorar
                um minuto.
              </p>
              <label className="flex items-center gap-2 text-sm font-bold">
                <input
                  type="radio"
                  checked={bossTipo === "temas"}
                  onChange={() => setBossTipo("temas")}
                />
                Temas específicos
              </label>
              <label className="flex items-center gap-2 text-sm font-bold">
                <input
                  type="radio"
                  checked={bossTipo === "global"}
                  onChange={() => setBossTipo("global")}
                />
                Exame global (programa completo)
              </label>
              {bossTipo === "temas" && (
                <input
                  className="w-full rounded-xl border-2 border-watty-border px-3 py-2"
                  value={bossTemasInput}
                  onChange={(e) => setBossTemasInput(e.target.value)}
                  placeholder={`Temas (ex.: ${ex})`}
                />
              )}
              <button
                type="button"
                disabled={busy}
                onClick={() => void gerarBoss()}
                className="rounded-xl bg-watty-btn px-4 py-2 font-black text-white disabled:opacity-50"
              >
                Gerar exame e iniciar
              </button>
            </>
          ) : (
            <>
              <BossTimer />
              <p className="text-xs text-slate-600">{bossTemasAtuais}</p>
              {bossConteudo.includes("===SOLUCOES===") ? (
                <>
                  <WattyMarkdownChart
                    text={bossConteudo.split("===SOLUCOES===")[0] ?? ""}
                  />
                  <details className="rounded-xl border border-watty-border bg-amber-50/50 p-3">
                    <summary className="cursor-pointer font-bold">
                      Ver correção
                    </summary>
                    <WattyMarkdownChart
                      text={
                        bossConteudo.split("===SOLUCOES===")[1] ?? ""
                      }
                    />
                  </details>
                  <button
                    type="button"
                    onClick={() => void concluirBoss()}
                    className="rounded-xl bg-watty-purple px-4 py-2 font-bold text-white"
                  >
                    Concluir (+500 XP)
                  </button>
                </>
              ) : (
                <>
                  <WattyMarkdownChart text={bossConteudo} />
                  <button
                    type="button"
                    onClick={() => setBossIniciado(false)}
                    className="text-sm font-bold text-slate-600 underline"
                  >
                    Voltar atrás
                  </button>
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
