import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import {
  SESSION_COOKIE,
  sessionCookieOptions,
  signSession,
} from "@/lib/session";

export const runtime = "nodejs";

/** Atualiza só o cookie (ex.: dica -5 XP) — igual ao Streamlit sem gravar folha. */
export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }
  const body = (await req.json()) as { delta?: number };
  const delta = Number(body.delta);
  if (!Number.isFinite(delta)) {
    return NextResponse.json({ error: "delta inválido" }, { status: 400 });
  }

  const xp = Math.max(0, session.xp + delta);
  const token = await signSession({ ...session, xp });
  const jar = await cookies();
  jar.set(SESSION_COOKIE, token, sessionCookieOptions());
  return NextResponse.json({ ok: true, session: { ...session, xp } });
}
