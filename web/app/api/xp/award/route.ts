import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import { updateProfileXpNivel } from "@/lib/sheets";
import {
  SESSION_COOKIE,
  sessionCookieOptions,
  signSession,
} from "@/lib/session";

export const runtime = "nodejs";

function nivelFromXp(xp: number) {
  return Math.floor(xp / 200) + 1;
}

/** Ganho de XP + gravação na folha Perfis (acao_jogo). */
export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }
  const body = (await req.json()) as { gained?: number };
  const gained = Math.max(0, Math.floor(Number(body.gained)));
  if (!Number.isFinite(gained)) {
    return NextResponse.json({ error: "gained inválido" }, { status: 400 });
  }

  const xp = session.xp + gained;
  const nivel = Math.max(session.nivel, nivelFromXp(xp));

  try {
    await updateProfileXpNivel(session.linha_bd, xp, nivel);
  } catch (e) {
    console.error("Sheets XP update:", e);
  }

  const nextSession = { ...session, xp, nivel };
  const token = await signSession(nextSession);
  const jar = await cookies();
  jar.set(SESSION_COOKIE, token, sessionCookieOptions());

  return NextResponse.json({
    ok: true,
    session: nextSession,
    levelUp: nivel > session.nivel,
  });
}
