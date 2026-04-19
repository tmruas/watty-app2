"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback } from "react";
import LoginWizardWeb from "@/components/login/LoginWizardWeb";
import { createClient } from "@/lib/supabase/client";

function LoginInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/chat";

  const onAuthenticated = useCallback(
    async (payload: {
      access_token: string;
      refresh_token: string;
      nome_display: string;
    }) => {
      const supabase = createClient();
      const { error } = await supabase.auth.setSession({
        access_token: payload.access_token,
        refresh_token: payload.refresh_token,
      });
      if (error) {
        console.error(error);
        return;
      }
      router.push(next.startsWith("/") ? next : "/chat");
      router.refresh();
    },
    [router, next]
  );

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";
  const emailRedirect =
    process.env.NEXT_PUBLIC_SUPABASE_EMAIL_REDIRECT_URL?.trim() || undefined;

  return (
    <LoginWizardWeb
      args={{
        supabase_url: url,
        supabase_anon_key: anon,
        supabase_email_redirect_url: emailRedirect,
      }}
      onAuthenticated={onAuthenticated}
    />
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center font-bold">A carregar…</div>}>
      <LoginInner />
    </Suspense>
  );
}
