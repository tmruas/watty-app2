"use client";

import { useCallback, useEffect, useState } from "react";
import { ANOS, MAIN_TABS, disciplinasParaAno } from "@/lib/constants";
import { createClient } from "@/lib/supabase/client";
import { nomeCurtoParaHud } from "@/lib/displayNome";
import type { SessionPayload } from "@/lib/types";
import type { WattyAuthPayload } from "@/components/login/LoginWizardWeb";
import { BossPanel } from "./BossPanel";
import { ChatPanel } from "./ChatPanel";
import { QuizPanel } from "./QuizPanel";
import { SummaryPanel } from "./SummaryPanel";
import { WattyPublicLanding } from "./WattyPublicLanding";
import { WattyTvPanel } from "./WattyTvPanel";

type MainTab = (typeof MAIN_TABS)[number]["id"];
type QuizSub = "treino" | "boss";

export function WattyApp() {
  const [session, setSession] = useState<SessionPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [loginBusy, setLoginBusy] = useState(false);
  const [gateError, setGateError] = useState<string | null>(null);
  const [gateKey, setGateKey] = useState(0);

  const [ano, setAno] = useState<string>(ANOS[0]);
  const [disciplina, setDisciplina] = useState(() => disciplinasParaAno(ANOS[0])[0]);
  const [tab, setTab] = useState<MainTab>("chat");
  const [quizSub, setQuizSub] = useState<QuizSub>("treino");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const refreshSession = useCallback(async () => {
    try {
      const res = await fetch("/api/session", { credentials: "include" });
      const data = (await res.json()) as { ok?: boolean; session?: SessionPayload };
      if (res.ok && data.session) setSession(data.session);
      else setSession(null);
    } catch {
      setSession(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const id = requestAnimationFrame(() => {
      void refreshSession();
    });
    return () => cancelAnimationFrame(id);
  }, [refreshSession]);

  /**
   * Depois do `LoginWizardWeb` (commit 7a102e6): sessão Supabase + perfil Google Sheets
   * via cookie JWT, como no resto desta app.
   */
  const onAuthenticated = useCallback(async (payload: WattyAuthPayload) => {
    const url = (process.env.NEXT_PUBLIC_SUPABASE_URL ?? "").trim();
    const anon = (process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "").trim();
    if (!url || !anon) {
      setGateError("Falta configurar o Supabase (URL e chave anon nas variáveis de ambiente).");
      setGateKey((k) => k + 1);
      return;
    }

    const supabase = createClient();
    const { error: sessionError } = await supabase.auth.setSession({
      access_token: payload.access_token,
      refresh_token: payload.refresh_token,
    });
    if (sessionError) {
      setGateError(sessionError.message);
      setGateKey((k) => k + 1);
      return;
    }

    const { data: userData } = await supabase.auth.getUser();
    const m = (userData.user?.user_metadata ?? {}) as Record<string, unknown>;
    const nomePart = typeof m.nome === "string" ? m.nome.trim() : "";
    const idadePart = typeof m.idade === "string" ? m.idade.trim() : "";
    const escolaPart = typeof m.escola_turma === "string" ? m.escola_turma.trim() : "";
    const nomeAluno =
      nomePart && idadePart && escolaPart
        ? `${nomePart} | ${idadePart} | ${escolaPart}`
        : (payload.nome_display || "Aluno").trim();

    setLoginBusy(true);
    setGateError(null);
    try {
      const res = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ nome: nomeAluno }),
      });
      const data = (await res.json()) as { session?: SessionPayload; error?: string };
      if (!res.ok) throw new Error(data.error || "Erro ao entrar");
      if (data.session) setSession(data.session);
    } catch (e) {
      setGateError(e instanceof Error ? e.message : "Erro ao entrar");
      setGateKey((k) => k + 1);
      await supabase.auth.signOut();
    } finally {
      setLoginBusy(false);
    }
  }, []);

  const logout = async () => {
    await fetch("/api/logout", { method: "POST", credentials: "include" });
    setSession(null);
    setGateKey((k) => k + 1);
    setGateError(null);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen w-full flex-col items-center justify-center gap-4 px-6">
        <span
          className="inline-block h-14 w-14 animate-spin rounded-full border-4 border-watty-border border-t-watty-btn"
          aria-hidden
        />
        <p className="text-center text-lg font-bold text-watty-purple">A carregar…</p>
      </div>
    );
  }

  if (!session) {
    return (
      <WattyPublicLanding
        gateKey={gateKey}
        loginBusy={loginBusy}
        gateError={gateError}
        onAuthenticated={onAuthenticated}
      />
    );
  }

  const nomeHud = nomeCurtoParaHud(session.nome_aluno);
  const discOpts = [...disciplinasParaAno(ano)];

  const sidebar = (
    <aside className="flex h-full w-full max-w-sm flex-col gap-4 border-watty-border bg-white p-4 text-watty-purple shadow-lg md:border-r-2">
      <div className="flex items-center justify-between md:hidden">
        <span className="font-black">Menu</span>
        <button
          type="button"
          className="rounded-lg border border-watty-border px-2 py-1 text-sm"
          onClick={() => setSidebarOpen(false)}
        >
          Fechar
        </button>
      </div>
      <div className="mx-auto hidden max-h-28 w-full max-w-[200px] md:block">
        <div className="flex h-24 items-center justify-center rounded-xl bg-watty-bg text-4xl font-black text-watty-btn">
          ⚡
        </div>
      </div>
      <h2 className="text-lg font-black">⚡ Menu do Watty</h2>
      <p className="rounded-lg bg-green-50 px-3 py-2 text-sm font-semibold text-green-900">👤 Olá, {nomeHud}!</p>
      <label className="block text-sm font-bold">
        🎓 Ano
        <select
          className="watty-input mt-1"
          value={ano}
          onChange={(e) => {
            const next = e.target.value;
            setAno(next);
            const opts = [...disciplinasParaAno(next)];
            if (!opts.includes(disciplina)) {
              setDisciplina(opts[0] ?? disciplina);
            }
          }}
        >
          {ANOS.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm font-bold">
        📚 Disciplina
        <select
          className="watty-input mt-1"
          value={disciplina}
          onChange={(e) => setDisciplina(e.target.value)}
        >
          {discOpts.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </label>
      <hr className="border-watty-border" />
      <nav className="flex flex-col gap-2">
        {MAIN_TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`rounded-xl px-4 py-3 text-left text-sm font-bold transition ${
              tab === t.id
                ? "bg-watty-btn text-white shadow-md"
                : "bg-watty-bg text-watty-purple hover:bg-watty-border/40"
            }`}
            onClick={() => {
              setTab(t.id);
              setSidebarOpen(false);
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <button
        type="button"
        className="mt-auto text-sm font-bold text-watty-btn-dark underline"
        onClick={() => void logout()}
      >
        Sair
      </button>
    </aside>
  );

  return (
    <div className="flex min-h-0 flex-1 flex-col md:flex-row">
      <button
        type="button"
        className="m-2 flex items-center gap-2 self-start rounded-xl border-2 border-watty-border bg-white px-3 py-2 font-bold text-watty-purple md:hidden"
        onClick={() => setSidebarOpen(true)}
      >
        ☰ Menu
      </button>

      {sidebarOpen && (
        <div className="fixed inset-0 z-40 flex md:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/40"
            aria-label="Fechar menu"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="relative z-50 h-full w-[min(88vw,340px)] overflow-y-auto">{sidebar}</div>
        </div>
      )}

      <div className="hidden w-[min(100%,320px)] shrink-0 md:block">{sidebar}</div>

      <main className="min-h-0 min-w-0 flex-1 overflow-y-auto p-4 md:p-8">
        <div className="mb-6 grid grid-cols-2 gap-2 sm:grid-cols-4">
          <div className="watty-metric">
            <div className="text-xs font-extrabold uppercase text-watty-btn-dark">👤 Jogador</div>
            <div className="truncate text-lg font-black text-watty-purple">{nomeHud}</div>
          </div>
          <div className="watty-metric">
            <div className="text-xs font-extrabold uppercase text-watty-btn-dark">🔰 Nível</div>
            <div className="text-2xl font-black text-watty-purple">Nvl {session.nivel}</div>
          </div>
          <div className="watty-metric">
            <div className="text-xs font-extrabold uppercase text-watty-btn-dark">🏆 XP</div>
            <div className="text-2xl font-black text-watty-purple">{session.xp}</div>
          </div>
          <div className="watty-metric">
            <div className="text-xs font-extrabold uppercase text-watty-btn-dark">🔥 Streak</div>
            <div className="text-2xl font-black text-watty-purple">{session.streak} dias</div>
          </div>
        </div>
        <hr className="mb-8 border-watty-border" />

        {tab === "chat" && (
          <ChatPanel
            key={`${ano}-${disciplina}`}
            session={session}
            ano={ano}
            disciplina={disciplina}
          />
        )}
        {tab === "quiz" && (
          <div className="space-y-6">
            <div className="flex flex-wrap gap-2 border-b-2 border-watty-border pb-2">
              <button
                type="button"
                className={`rounded-full px-4 py-2 text-sm font-bold ${
                  quizSub === "treino" ? "bg-watty-btn text-white" : "bg-white text-watty-purple"
                }`}
                onClick={() => setQuizSub("treino")}
              >
                ⚡ Treino rápido
              </button>
              <button
                type="button"
                className={`rounded-full px-4 py-2 text-sm font-bold ${
                  quizSub === "boss" ? "bg-watty-btn text-white" : "bg-white text-watty-purple"
                }`}
                onClick={() => setQuizSub("boss")}
              >
                ⚔️ Boss Battle
              </button>
            </div>
            {quizSub === "treino" ? (
              <QuizPanel
                session={session}
                ano={ano}
                disciplina={disciplina}
                onSessionUpdate={setSession}
              />
            ) : (
              <BossPanel ano={ano} disciplina={disciplina} onSessionUpdate={setSession} />
            )}
          </div>
        )}
        {tab === "resumos" && <SummaryPanel ano={ano} disciplina={disciplina} />}
        {tab === "watty-tv" && <WattyTvPanel />}
      </main>
    </div>
  );
}
