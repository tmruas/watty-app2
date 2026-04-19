"use client";

import Link from "next/link";
import { GAMES_ROWS } from "@/lib/games";

export default function JogosPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-black text-watty-purple">Biblioteca de jogos</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {GAMES_ROWS.map((g) => (
          <Link
            key={g.filename}
            href={`/jogos/play?file=${encodeURIComponent(g.filename)}`}
            className="group flex min-h-[8rem] flex-col justify-end rounded-2xl border-2 border-watty-border p-4 text-white shadow-md transition hover:scale-[1.02]"
            style={{ background: g.cover }}
          >
            <span className="text-sm font-black drop-shadow-md">{g.title}</span>
            <span className="mt-2 text-xs font-bold opacity-90">Jogar →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
