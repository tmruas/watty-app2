"use client";

import { useCallback, useEffect, useState } from "react";
import { WattyMarkdownChart } from "@/components/WattyMarkdownChart";
import { useWattyUi } from "@/components/AppShell";

type Msg = { role: "user" | "assistant"; content: string };

export default function ChatPage() {
  const { ano, disciplina } = useWattyUi();
  const [messages, setMessages] = useState<Msg[]>(() => [
    {
      role: "assistant",
      content: `Olá! Sou o teu tutor de ${disciplina}. Que desafio vamos resolver hoje?`,
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content: `Olá! Sou o teu tutor de ${disciplina}. Que desafio vamos resolver hoje?`,
      },
    ]);
    setErr(null);
  }, [ano, disciplina]);

  const send = useCallback(async () => {
    const t = input.trim();
    if (!t || busy) return;
    setErr(null);
    setInput("");
    const nextUser: Msg = { role: "user", content: t };
    setMessages((m) => [...m, nextUser]);
    setBusy(true);
    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          ano,
          disciplina,
          userMessage: t,
          history: [...messages, nextUser].slice(-6),
        }),
      });
      const data = (await res.json()) as { text?: string; error?: string };
      if (!res.ok) throw new Error(data.error ?? "Erro no servidor");
      setMessages((m) => [
        ...m,
        { role: "assistant", content: data.text ?? "" },
      ]);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
      setMessages((m) => m.slice(0, -1));
    } finally {
      setBusy(false);
    }
  }, [ano, disciplina, input, busy, messages]);

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-black text-watty-purple">
        Chat socrático — {disciplina}
      </h1>
      <p className="text-sm font-medium text-slate-600">
        Pergunta-me algo sobre a matéria do {ano}.
      </p>

      <div className="space-y-4 rounded-2xl border border-watty-border bg-white/90 p-4 shadow-sm">
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.role === "user"
                ? "ml-8 rounded-xl bg-watty-bg px-3 py-2"
                : "mr-4 border-l-4 border-watty-btn pl-3"
            }
          >
            {m.role === "assistant" ? (
              <WattyMarkdownChart text={m.content} />
            ) : (
              <p className="whitespace-pre-wrap font-medium">{m.content}</p>
            )}
          </div>
        ))}
        {busy && (
          <p className="text-sm font-semibold text-watty-purple">A pensar…</p>
        )}
        {err && <p className="text-sm font-bold text-red-600">{err}</p>}
      </div>

      <div className="flex gap-2">
        <input
          className="min-h-[48px] flex-1 rounded-xl border-2 border-watty-border px-3 font-semibold text-watty-purple outline-none focus:border-watty-accent"
          placeholder="Escreve a tua dúvida…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && void send()}
          disabled={busy}
        />
        <button
          type="button"
          onClick={() => void send()}
          disabled={busy || !input.trim()}
          className="rounded-xl bg-watty-btn px-5 py-2 font-black uppercase tracking-wide text-white shadow-watty disabled:opacity-50"
        >
          Enviar
        </button>
      </div>
    </div>
  );
}
