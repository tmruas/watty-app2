"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { ALLOWED_GAME_FILES } from "@/lib/games";

function PlayInner() {
  const sp = useSearchParams();
  const file = sp.get("file") ?? "";
  const ok = ALLOWED_GAME_FILES.has(file);
  const src = ok ? `/jogos/${encodeURIComponent(file)}` : "";

  if (!ok) {
    return (
      <div className="space-y-4">
        <p className="font-bold text-red-700">Jogo inválido ou em falta.</p>
        <Link href="/jogos" className="text-watty-purple underline">
          Voltar à biblioteca
        </Link>
      </div>
    );
  }

  return (
    <div className="flex h-[min(85vh,48rem)] flex-col gap-3">
      <div className="flex items-center justify-between gap-2">
        <Link
          href="/jogos"
          className="text-sm font-bold text-watty-purple hover:underline"
        >
          ← Biblioteca
        </Link>
      </div>
      <iframe
        title={file}
        src={src}
        className="min-h-0 w-full flex-1 rounded-xl border border-watty-border bg-white"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}

export default function JogoPlayPage() {
  return (
    <Suspense fallback={<p className="font-semibold">A carregar…</p>}>
      <PlayInner />
    </Suspense>
  );
}
