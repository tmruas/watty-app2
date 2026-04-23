import { SignJWT, jwtVerify } from "jose";

export const SESSION_COOKIE = "watty_session";

export type SessionPayload = {
  nome_aluno: string;
  linha_bd: number;
  xp: number;
  nivel: number;
  streak: number;
};

function getSecretKey() {
  const raw = process.env.SESSION_SECRET;
  if (!raw || raw.length < 16) {
    throw new Error(
      "SESSION_SECRET must be set (min 16 chars) for signed sessions",
    );
  }
  return new TextEncoder().encode(raw);
}

export async function signSession(payload: SessionPayload): Promise<string> {
  return new SignJWT({ ...payload })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("30d")
    .sign(getSecretKey());
}

export async function verifySession(
  token: string | undefined,
): Promise<SessionPayload | null> {
  if (!token) return null;
  try {
    const { payload } = await jwtVerify(token, getSecretKey());
    const nome_aluno = String(payload.nome_aluno ?? "");
    const linha_bd = Number(payload.linha_bd);
    const xp = Number(payload.xp);
    const nivel = Number(payload.nivel);
    const streak = Number(payload.streak);
    if (!nome_aluno || !Number.isFinite(linha_bd)) return null;
    return {
      nome_aluno,
      linha_bd,
      xp: Number.isFinite(xp) ? xp : 0,
      nivel: Number.isFinite(nivel) ? nivel : 1,
      streak: Number.isFinite(streak) ? streak : 1,
    };
  } catch {
    return null;
  }
}

export function sessionCookieOptions() {
  const isProd = process.env.NODE_ENV === "production";
  return {
    httpOnly: true as const,
    secure: isProd,
    sameSite: "lax" as const,
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  };
}
