"use client";

import { useCallback, useMemo, useState } from "react";
import { AssistantBody } from "./AssistantBody";
import type { ChatMessage, SessionPayload } from "@/lib/types";

function chatKey(ano: string, disc: string) {
  return `watty_chat_${ano}_${disc}`;
}

function defaultIntro(disciplina: string): ChatMessage[] {
  return [
    {
      role: "assistant",
      content: `Olá! ⚡ Sou o teu tutor de ${disciplina}. Que desafio vamos resolver hoje?`,
    },
  ];
}

export function ChatPanel({
  session: _session,
  ano,
  disciplina,
}: {
  session: SessionPayload;
  ano: string;
  disciplina: string;
}) {
  void _session;
  const storageKey = useMemo(() => chatKey(ano, disciplina), [ano, disciplina]);

  const loadFromStorage = useCallback((): ChatMessage[] => {
    if (typeof window === "undefined") return defaultIntro(disciplina);
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        const parsed = JSON.parse(raw) as ChatMessage[];
        if (Array.isArray(parsed) && parsed.length) return parsed;
      }
    } catch {
      /* ignore */
    }
    return defaultIntro(disciplina);
  }, [storageKey, disciplina]);

  const [messages, setMessages] = useState<ChatMessage[]>(() => loadFromStorage());

  const persist = useCallback(
    (next: ChatMessage[]) => {
      setMessages(next);
      try {
        localStorage.setItem(storageKey, JSON.stringify(next));
      } catch {
        /* ignore */
      }
    },
    [storageKey],
  );

  const [input, setInput] = useState("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageMime, setImageMime] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const onFile = (f: File | null) => {
    if (!f) {
      setImagePreview(null);
      setImageMime(null);
      setImageBase64(null);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const res = reader.result as string;
      const base64 = res.split(",")[1] ?? res;
      setImagePreview(res);
      setImageMime(f.type || "image/jpeg");
      setImageBase64(base64);
    };
    reader.readAsDataURL(f);
  };

  const send = async () => {
    const q = input.trim();
    if (!q || busy) return;
    setErr(null);
    setBusy(true);
    const userMsg: ChatMessage = { role: "user", content: q };
    const nextAfterUser = [...messages, userMsg];
    persist(nextAfterUser);
    setInput("");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          messages: nextAfterUser,
          disciplina,
          ano,
          question: q,
          imageBase64: imageBase64 ?? undefined,
          imageMimeType: imageMime ?? undefined,
        }),
      });
      const data = (await res.json()) as { text?: string; error?: string };
      if (!res.ok) throw new Error(data.error || "Erro no chat");
      const assistant: ChatMessage = {
        role: "assistant",
        content: data.text ?? "",
      };
      persist([...nextAfterUser, assistant]);
      setImagePreview(null);
      setImageBase64(null);
      setImageMime(null);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Erro");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#4A148C] md:text-3xl">
        💬 O Super Tutor de {disciplina}
      </h1>
      <p className="font-medium text-[#311B52]">
        Pergunta-me algo ou envia uma foto do teu exercício!
      </p>

      <label className="block text-sm font-bold text-[#4A148C]">
        📸 Foto do exercício (opcional)
        <input
          type="file"
          accept="image/jpeg,image/png,image/jpg"
          className="mt-1 block w-full text-sm"
          onChange={(e) => onFile(e.target.files?.[0] ?? null)}
        />
      </label>
      {imagePreview && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={imagePreview} alt="Pré-visualização" className="max-h-56 rounded-xl border-2 border-[#D1C4E9]" />
      )}

      <div className="max-h-[55vh] space-y-3 overflow-y-auto rounded-2xl border-2 border-[#D1C4E9] bg-white/80 p-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[95%] rounded-2xl px-4 py-2 ${
                m.role === "user"
                  ? "bg-[#9C27B0] text-white"
                  : "bg-[#F3E5F5] text-[#311B52]"
              }`}
            >
              {m.role === "assistant" ? (
                <AssistantBody text={m.content} />
              ) : (
                <p className="whitespace-pre-wrap font-medium">{m.content}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {err && (
        <p className="rounded-lg bg-red-100 px-3 py-2 text-sm text-red-800">{err}</p>
      )}

      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) void send();
          }}
          placeholder="Escreve a tua dúvida aqui..."
          className="watty-input flex-1"
          disabled={busy}
        />
        <button type="button" className="watty-btn shrink-0" disabled={busy} onClick={() => void send()}>
          {busy ? "…" : "Enviar"}
        </button>
      </div>
    </div>
  );
}
