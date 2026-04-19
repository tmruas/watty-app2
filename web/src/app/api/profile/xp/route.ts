import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { atualizarXpNivel, verifyPerfilLinha } from "@/lib/sheets";
import { createClient } from "@/lib/supabase/server";

const bodySchema = z.object({
  xp: z.number().int().min(0),
  nivel: z.number().int().min(1),
  linha_bd: z.number().int().min(2),
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

    const json = await request.json();
    const body = bodySchema.parse(json);

    const ok = await verifyPerfilLinha(user.email, body.linha_bd);
    if (!ok) {
      return NextResponse.json({ error: "Linha inválida." }, { status: 403 });
    }

    await atualizarXpNivel(body.linha_bd, body.xp, body.nivel);
    return NextResponse.json({ ok: true });
  } catch (e) {
    if (e instanceof z.ZodError) {
      return NextResponse.json({ error: "Pedido inválido.", details: e.flatten() }, { status: 400 });
    }
    console.error(e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Erro ao atualizar." },
      { status: 500 }
    );
  }
}
