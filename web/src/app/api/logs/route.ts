import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { guardarNoExcel } from "@/lib/sheets";
import { forwardToPythonBackend, hasPythonBackendConfigured } from "@/lib/python-backend";
import { createClient } from "@/lib/supabase/server";

const bodySchema = z.object({
  aba: z.string().min(1),
  tema: z.string().min(1),
  resposta_ia: z.string(),
  ano: z.string().min(1),
  disciplina: z.string().min(1),
});

export async function POST(request: NextRequest) {
  try {
    if (hasPythonBackendConfigured()) {
      const body = bodySchema.parse(await request.json());
      const upstream = await forwardToPythonBackend("/api/logs", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      const payload = await upstream.json();
      return NextResponse.json(payload, { status: upstream.status });
    }

    const supabase = await createClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user?.email) {
      return NextResponse.json({ error: "Não autenticado." }, { status: 401 });
    }

    const body = bodySchema.parse(await request.json());
    await guardarNoExcel(
      body.aba,
      body.tema,
      body.resposta_ia,
      body.ano,
      body.disciplina,
      user.email
    );
    return NextResponse.json({ ok: true });
  } catch (e) {
    if (e instanceof z.ZodError) {
      return NextResponse.json({ error: "Pedido inválido." }, { status: 400 });
    }
    console.error(e);
    return NextResponse.json({ error: "Erro ao gravar log." }, { status: 500 });
  }
}
