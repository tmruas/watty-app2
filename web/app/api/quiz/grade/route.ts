import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import { generateText, stripModelJson } from "@/lib/gemini";
import { buildGradePrompt } from "@/lib/prompts";

export const runtime = "nodejs";
export const maxDuration = 120;

export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }

  const body = (await req.json()) as {
    disciplina?: string;
    ano?: string;
    pergunta?: string;
    resposta_modelo?: string;
    criterios?: string;
    pontos?: number;
    respostaAluno?: string;
  };

  const disciplina = body.disciplina ?? "";
  const ano = body.ano ?? "";
  const pergunta = body.pergunta ?? "";
  const respostaAluno = (body.respostaAluno ?? "").trim();
  const pontos = Number(body.pontos) || 10;

  if (!disciplina || !ano || !pergunta || respostaAluno.length < 5) {
    return NextResponse.json({ error: "Dados de correção em falta" }, { status: 400 });
  }

  try {
    const raw = await generateText(
      buildGradePrompt(disciplina, ano, {
        pergunta,
        resposta_modelo: body.resposta_modelo,
        criterios: body.criterios,
        pontos,
      }, respostaAluno),
    );
    const correcao = JSON.parse(stripModelJson(raw)) as {
      nota?: number;
      feedback?: string;
      resposta_modelo?: string;
    };
    return NextResponse.json({ ok: true, correcao });
  } catch (e) {
    console.error(e);
    const msg = e instanceof Error ? e.message : "Erro na correção";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
