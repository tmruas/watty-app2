import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import { generateText, stripModelJson } from "@/lib/gemini";
import { buildQuizPrompt } from "@/lib/prompts";

export const runtime = "nodejs";
export const maxDuration = 120;

export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }

  const body = (await req.json()) as {
    tema?: string;
    ano?: string;
    disciplina?: string;
  };
  const tema = (body.tema ?? "").trim();
  const ano = (body.ano ?? "").trim();
  const disciplina = (body.disciplina ?? "").trim();
  if (!tema || !ano || !disciplina) {
    return NextResponse.json({ error: "tema, ano e disciplina obrigatórios" }, { status: 400 });
  }

  try {
    const raw = await generateText(buildQuizPrompt(tema, ano, disciplina));
    const texto = stripModelJson(raw);
    const quiz = JSON.parse(texto) as unknown;
    return NextResponse.json({ ok: true, quiz });
  } catch (e) {
    console.error(e);
    const msg = e instanceof Error ? e.message : "Erro ao gerar quiz";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
