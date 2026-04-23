import { NextResponse } from "next/server";
import { getSessionFromCookies } from "@/lib/api-auth";
import { appendActivityLog } from "@/lib/sheets";
import { generateText } from "@/lib/gemini";
import { buildChatSystemPrompt } from "@/lib/prompts";

export const runtime = "nodejs";
export const maxDuration = 120;

export async function POST(req: Request) {
  const session = await getSessionFromCookies();
  if (!session) {
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  }

  const body = (await req.json()) as {
    messages?: { role: string; content: string }[];
    disciplina?: string;
    ano?: string;
    question?: string;
    imageBase64?: string | null;
    imageMimeType?: string | null;
  };

  const disciplina = body.disciplina?.trim() ?? "";
  const ano = body.ano?.trim() ?? "";
  const question = body.question?.trim() ?? "";
  const messages = body.messages ?? [];

  if (!disciplina || !ano || !question) {
    return NextResponse.json(
      { error: "disciplina, ano e question são obrigatórios" },
      { status: 400 },
    );
  }

  const system = buildChatSystemPrompt(disciplina, ano);
  const recent = messages.slice(-4);
  const historyText = recent
    .map((m) => `${m.role}: ${m.content}`)
    .join("\n\n");

  const textBlock = `${system}

---
Histórico recente:
${historyText}

Pergunta do aluno: ${question}`;

  const parts: Array<{ text?: string; inlineData?: { mimeType: string; data: string } }> = [
    { text: textBlock },
  ];

  if (body.imageBase64 && body.imageMimeType) {
    parts.push({
      inlineData: {
        mimeType: body.imageMimeType,
        data: body.imageBase64,
      },
    });
  }

  try {
    const reply = await generateText({
      role: "user",
      parts,
    });

    try {
      await appendActivityLog({
        nome: session.nome_aluno,
        ano,
        disciplina,
        aba: "Chat",
        tema: question,
        resposta: reply,
      });
    } catch (e) {
      console.error("log chat:", e);
    }

    return NextResponse.json({ ok: true, text: reply });
  } catch (e) {
    console.error(e);
    const msg = e instanceof Error ? e.message : "Erro na IA";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
