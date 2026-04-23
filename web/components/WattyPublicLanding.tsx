"use client";

import LoginWizardWeb, { type WattyAuthPayload } from "@/components/login/LoginWizardWeb";

type WattyPublicLandingProps = {
  gateKey: number;
  loginBusy: boolean;
  gateError: string | null;
  onAuthenticated: (payload: WattyAuthPayload) => Promise<void>;
};

/**
 * Landing e fluxo de registo/entrada iguais ao commit `bcca015`
 * (pai de `7a102e6`; `LoginWizardWeb.tsx` é idêntico entre os dois — só mudou o `wattyvid2.mp4`).
 */
export function WattyPublicLanding({
  gateKey,
  loginBusy,
  gateError,
  onAuthenticated,
}: WattyPublicLandingProps) {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";
  const emailRedirect =
    process.env.NEXT_PUBLIC_SUPABASE_EMAIL_REDIRECT_URL?.trim() || undefined;

  return (
    <div className="min-h-full min-h-screen bg-white text-watty-ink">
      {gateError ? (
        <p
          role="alert"
          className="mx-auto max-w-lg px-4 pt-6 text-center text-sm font-semibold text-red-700"
        >
          {gateError}
        </p>
      ) : null}
      <LoginWizardWeb
        key={gateKey}
        disabled={loginBusy}
        args={{
          supabase_url: url,
          supabase_anon_key: anon,
          supabase_email_redirect_url: emailRedirect,
        }}
        onAuthenticated={onAuthenticated}
      />
    </div>
  );
}
