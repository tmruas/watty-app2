import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import { generateText } from "@/lib/gemini";
import { buildExamPrompt } from "@/lib/prompts";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }

  const body = (await req.json()) as {
    disciplina?: string;
    ano?: string;
    temas?: string;
  };
  const disciplina = (body.disciplina ?? "").trim();
  const ano = (body.ano ?? "").trim();
  const temas = (body.temas ?? "").trim();
  if (!disciplina || !ano || !temas) {
    return NextResponse.json({ error: "disciplina, ano e temas obrigatórios" }, { status: 400 });
  }

  try {
    const raw = await generateText(buildExamPrompt(disciplina, ano, temas));
    const texto = raw
      .replace(/🔸/g, "\n\n🔸")
      .replace(/\n---/g, "\n\n---\n");
    return NextResponse.json({ ok: true, text: texto });
  } catch (e) {
    console.error(e);
    const msg = e instanceof Error ? e.message : "Erro ao gerar exame";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
