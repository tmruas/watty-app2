import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { loadOrCreateProfile } from "@/lib/sheets";
import {
  SESSION_COOKIE,
  sessionCookieOptions,
  signSession,
} from "@/lib/session";

export const runtime = "nodejs";

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as { nome?: string };
    const nome = (body.nome ?? "").trim();
    if (!nome) {
      return NextResponse.json({ error: "Nome em falta" }, { status: 400 });
    }

    const { xp, nivel, streak, linha_bd } = await loadOrCreateProfile(nome);
    const token = await signSession({
      nome_aluno: nome,
      linha_bd,
      xp,
      nivel,
      streak,
    });

    const jar = await cookies();
    jar.set(SESSION_COOKIE, token, sessionCookieOptions());

    return NextResponse.json({
      ok: true,
      session: { nome_aluno: nome, linha_bd, xp, nivel, streak },
    });
  } catch (e) {
    console.error(e);
    const msg = e instanceof Error ? e.message : "Erro ao carregar perfil";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
