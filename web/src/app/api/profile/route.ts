import { NextResponse } from "next/server";
import { carregarPerfil } from "@/lib/sheets";
import { forwardToPythonBackend, hasPythonBackendConfigured } from "@/lib/python-backend";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
  try {
    if (hasPythonBackendConfigured()) {
      const upstream = await forwardToPythonBackend("/api/profile", {
        method: "GET",
      });
      const payload = await upstream.json();
      return NextResponse.json(payload, { status: upstream.status });
    }

    const supabase = await createClient();
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser();
    if (error || !user?.email) {
      return NextResponse.json({ error: "Não autenticado." }, { status: 401 });
    }

    const perfil = await carregarPerfil(user.email);
    const meta = (user.user_metadata ?? {}) as Record<string, unknown>;
    const nome_display =
      (typeof meta.nome_display === "string" && meta.nome_display.trim()) ||
      (typeof meta.nome === "string" && meta.nome.trim()) ||
      user.email.split("@")[0] ||
      "Aluno";

    return NextResponse.json({
      email: user.email,
      nome_display,
      xp: perfil.xp,
      nivel: perfil.nivel,
      streak: perfil.streak,
      linha_bd: perfil.linha_bd,
      user_created_at: user.created_at ?? null,
    });
  } catch (e) {
    console.error(e);
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Erro ao carregar perfil." },
      { status: 500 }
    );
  }
}
