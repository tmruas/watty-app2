import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { buildChatSystemPrompt } from "@/lib/prompts";
import { generateContentText } from "@/lib/gemini";
import { guardarNoExcel } from "@/lib/sheets";
import { createClient } from "@/lib/supabase/server";

const bodySchema = z.object({
  ano: z.string(),
  disciplina: z.string(),
  userMessage: z.string().min(1),
  history: z
    .array(
      z.object({
        role: z.enum(["user", "assistant"]),
        content: z.string(),
      })
    )
    .max(20),
});

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user?.email) {
      return NextResponse.json({ error: "Não autenticado." }, { status: 401 });
    }

    const body = bodySchema.parse(await request.json());
    const system = buildChatSystemPrompt(body.disciplina, body.ano);
    const recent = body.history.slice(-4);
    const parts: string[] = [system];
    for (const m of recent) {
      parts.push(`${m.role}: ${m.content}`);
    }
    parts.push(`Pergunta do aluno: ${body.userMessage}`);
    const prompt = parts.join("\n\n");

    const text = await generateContentText(prompt);

    await guardarNoExcel(
      "Chat",
      body.userMessage,
      text,
      body.ano,
      body.disciplina,
      user.email
    );

    return NextResponse.json({ text });
  } catch (e) {
    if (e instanceof z.ZodError) {
      return NextResponse.json({ error: "Pedido inválido." }, { status: 400 });
    }
    console.error(e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Erro na IA." },
      { status: 500 }
    );
  }
}
