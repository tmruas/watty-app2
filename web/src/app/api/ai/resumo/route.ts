import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { buildResumoPrompt } from "@/lib/prompts";
import { generateContentText } from "@/lib/gemini";
import { guardarNoExcel } from "@/lib/sheets";
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
    const prompt = buildResumoPrompt(body.tema, body.disciplina, body.ano);
    const text = await generateContentText(prompt);

    await guardarNoExcel(
      "Resumo",
      body.tema,
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
