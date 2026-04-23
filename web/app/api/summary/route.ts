import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import { appendActivityLog } from "@/lib/sheets";
import { generateText } from "@/lib/gemini";
import { buildSummaryPrompt } from "@/lib/prompts";

export const runtime = "nodejs";
export const maxDuration = 120;

export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }

  const body = (await req.json()) as {
    tema?: string;
    disciplina?: string;
    ano?: string;
  };
  const tema = (body.tema ?? "").trim();
  const disciplina = (body.disciplina ?? "").trim();
  const ano = (body.ano ?? "").trim();
  if (!tema || !disciplina || !ano) {
    return NextResponse.json({ error: "tema, disciplina e ano obrigatórios" }, { status: 400 });
  }

  try {
    const text = await generateText(buildSummaryPrompt(tema, disciplina, ano));
    try {
      await appendActivityLog({
        nome: session.nome_aluno,
        ano,
        disciplina,
        aba: "Resumo",
        tema,
        resposta: text,
      });
    } catch (e) {
      console.error("log resumo:", e);
    }
    return NextResponse.json({ ok: true, text });
  } catch (e) {
    console.error(e);
    const msg = e instanceof Error ? e.message : "Erro";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
