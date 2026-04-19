import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { promptCorrecaoRespostaAberta } from "@/lib/prompts";
import { generateContentText } from "@/lib/gemini";
import { stripJsonFence } from "@/lib/json-ai";
import { createClient } from "@/lib/supabase/server";

const bodySchema = z.object({
  ano: z.string(),
  disciplina: z.string(),
  question: z.record(z.string(), z.any()),
  resposta_aluno: z.string().min(1),
  pontos_pergunta: z.number().int().positive(),
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
    const prompt = promptCorrecaoRespostaAberta(
      body.disciplina,
      body.ano,
      body.question,
      body.resposta_aluno,
      body.pontos_pergunta
    );
    const raw = await generateContentText(prompt);
    const texto = stripJsonFence(raw);
    const correcao = JSON.parse(texto) as {
      nota?: number;
      feedback?: string;
      resposta_modelo?: string;
    };
    return NextResponse.json({ correcao });
  } catch (e) {
    if (e instanceof z.ZodError) {
      return NextResponse.json({ error: "Pedido inválido." }, { status: 400 });
    }
    console.error(e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Erro na correção." },
      { status: 500 }
    );
  }
}
