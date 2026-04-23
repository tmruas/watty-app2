import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";

export const runtime = "nodejs";

export async function GET() {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ ok: false, session: null }, { status: 401 });
  }
  return NextResponse.json({ ok: true, session });
}
