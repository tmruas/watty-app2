import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { buildPromptExame } from "@/lib/exam-prompts";
import { generateContentText } from "@/lib/gemini";
import { createClient } from "@/lib/supabase/server";

const bodySchema = z.object({
  ano: z.string(),
  disciplina: z.string(),
  temas: z.string().min(1),
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
    const prompt = buildPromptExame(body.disciplina, body.ano, body.temas);
    const text = await generateContentText(prompt);
    const formatted = text
      .replace(/🔸/g, "\n\n🔸")
      .replace(/\n---/g, "\n\n---\n");
    return NextResponse.json({ text: formatted });
  } catch (e) {
    if (e instanceof z.ZodError) {
      return NextResponse.json({ error: "Pedido inválido." }, { status: 400 });
    }
    console.error(e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Erro ao gerar exame." },
      { status: 500 }
    );
  }
}
