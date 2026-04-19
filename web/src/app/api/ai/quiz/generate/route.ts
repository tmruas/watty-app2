import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { promptQuizMisto } from "@/lib/prompts";
import { generateContentText } from "@/lib/gemini";
import { stripJsonFence } from "@/lib/json-ai";
import { createClient } from "@/lib/supabase/server";

const bodySchema = z.object({
  ano: z.string(),
  disciplina: z.string(),
  tema: z.string().min(1),
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
    const prompt = promptQuizMisto(body.tema, body.ano, body.disciplina);
    const raw = await generateContentText(prompt);
    const texto = stripJsonFence(raw);
    const quiz = JSON.parse(texto) as unknown[];
    if (!Array.isArray(quiz)) {
      throw new Error("Resposta da IA não é um array.");
    }
    return NextResponse.json({ quiz });
  } catch (e) {
    if (e instanceof z.ZodError) {
      return NextResponse.json({ error: "Pedido inválido." }, { status: 400 });
    }
    console.error(e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Erro ao gerar quiz." },
      { status: 500 }
    );
  }
}
