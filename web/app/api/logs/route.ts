import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import { appendActivityLog } from "@/lib/sheets";

export const runtime = "nodejs";

export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }
  const body = (await req.json()) as {
    ano?: string;
    disciplina?: string;
    aba?: string;
    tema?: string;
    resposta?: string;
  };
  const ano = body.ano ?? "";
  const disciplina = body.disciplina ?? "";
  const aba = body.aba ?? "";
  const tema = body.tema ?? "";
  const resposta = body.resposta ?? "";
  if (!ano || !disciplina) {
    return NextResponse.json({ error: "ano/disciplina em falta" }, { status: 400 });
  }

  try {
    await appendActivityLog({
      nome: session.nome_aluno,
      ano,
      disciplina,
      aba,
      tema,
      resposta,
    });
    return NextResponse.json({ ok: true });
  } catch (e) {
    console.error(e);
    return NextResponse.json({ error: "Falha ao gravar log" }, { status: 500 });
  }
}
