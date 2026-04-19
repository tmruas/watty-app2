"use client";

import Link from "next/link";
import { useWattyProfile } from "@/context/WattyProfileContext";

function joinLinePt(createdAt: string | null): string {
  if (!createdAt) return "Bem-vindo ao Watty.";
  const d = new Date(createdAt);
  if (Number.isNaN(d.getTime())) return "Bem-vindo ao Watty.";
  const months = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
  ];
  return `Por aqui desde ${months[d.getMonth()]} de ${d.getFullYear()}`;
}

export default function PerfilPage() {
  const { profile } = useWattyProfile();
  if (!profile) return null;

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <Link
        href="/chat"
        className="inline-block text-sm font-bold text-watty-purple hover:underline"
      >
        ← Voltar
      </Link>
      <div className="rounded-3xl border-2 border-watty-border bg-white p-6 shadow-card">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-watty-bg text-2xl font-black text-watty-purple">
            {profile.nome_display
              .split(/\s+/)
              .filter(Boolean)
              .slice(0, 2)
              .map((p) => p[0]?.toUpperCase())
              .join("") || "?"}
          </div>
          <div>
            <h1 className="text-xl font-black text-watty-purple">
              {profile.nome_display}
            </h1>
            <p className="text-sm text-slate-600">{profile.email}</p>
            <p className="text-xs text-slate-500">
              {joinLinePt(profile.user_created_at)}
            </p>
          </div>
        </div>
        <div className="mt-6 grid grid-cols-3 gap-3 text-center">
          <div className="rounded-xl bg-watty-bg p-3">
            <div className="text-2xl">⚡</div>
            <div className="text-lg font-black text-watty-purple">
              {profile.xp}
            </div>
            <div className="text-xs font-bold text-slate-600">XP</div>
          </div>
          <div className="rounded-xl bg-watty-bg p-3">
            <div className="text-2xl">🛡️</div>
            <div className="text-lg font-black text-watty-purple">
              {profile.nivel}
            </div>
            <div className="text-xs font-bold text-slate-600">Nível</div>
          </div>
          <div className="rounded-xl bg-watty-bg p-3">
            <div className="text-2xl">🔥</div>
            <div className="text-lg font-black text-watty-purple">
              {profile.streak}
            </div>
            <div className="text-xs font-bold text-slate-600">Streak</div>
          </div>
        </div>
      </div>
    </div>
  );
}
