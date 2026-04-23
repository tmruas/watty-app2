import { createBrowserClient } from "@supabase/ssr";

/** Igual a `web/src/lib/supabase/client.ts` no commit `bcca015`. */
export function createClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL?.trim();
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.trim();
  if (!url || !anon) {
    throw new Error("NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY são obrigatórios.");
  }
  return createBrowserClient(url, anon);
}
