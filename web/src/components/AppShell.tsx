"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { createClient } from "@/lib/supabase/client";
import {
  LISTA_ANOS,
  disciplinasParaAno,
  FOOTER_EMAIL_AJUDA,
  FOOTER_URL_LINKEDIN,
} from "@/lib/watty-config";
import { useWattyProfile } from "@/context/WattyProfileContext";

const LS_KEY = "watty:ui:v1";

type UiPersist = { ano: string; disciplina: string };

function readPersist(): Partial<UiPersist> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as Partial<UiPersist>;
  } catch {
    return {};
  }
}

function writePersist(v: UiPersist) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(v));
  } catch {
    /* ignore */
  }
}

const nav = [
  { href: "/chat", label: "Aprender", key: "chat", emoji: "💬" },
  { href: "/quiz", label: "Treinar", key: "quiz", emoji: "🏋️" },
  { href: "/resumos", label: "Resumos", key: "resumos", emoji: "📚" },
  { href: "/jogos", label: "Jogos", key: "jogos", emoji: "🎮" },
  { href: "/watty-tv", label: "Watty TV", key: "watty_tv", emoji: "📺" },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { profile, loading, error, refresh } = useWattyProfile();

  const persisted = useMemo(() => readPersist(), []);
  const [ano, setAno] = useState(persisted.ano ?? LISTA_ANOS[2]);
  const discDefault = disciplinasParaAno(persisted.ano ?? LISTA_ANOS[2])[0];
  const [disciplina, setDisciplina] = useState(
    persisted.disciplina ?? discDefault
  );

  useEffect(() => {
    const d = disciplinasParaAno(ano);
    if (!d.includes(disciplina)) {
      setDisciplina(d[0] ?? disciplina);
    }
  }, [ano, disciplina]);

  useEffect(() => {
    writePersist({ ano, disciplina });
  }, [ano, disciplina]);

  const activeNav = useMemo(() => {
    const p = pathname ?? "";
    if (p.startsWith("/jogos")) return "jogos";
    if (p.startsWith("/watty-tv")) return "watty_tv";
    if (p.startsWith("/quiz")) return "quiz";
    if (p.startsWith("/resumos")) return "resumos";
    if (p.startsWith("/chat")) return "chat";
    return "chat";
  }, [pathname]);

  const logout = useCallback(async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }, [router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-watty-bg text-watty-purple">
        <div className="text-center font-bold">A carregar o Watty…</div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-watty-bg p-6 text-center">
        <p className="font-semibold text-red-700">{error ?? "Sessão inválida."}</p>
        <button
          type="button"
          onClick={() => void refresh()}
          className="rounded-xl bg-watty-btn px-4 py-2 font-bold text-white"
        >
          Tentar de novo
        </button>
        <Link href="/login" className="text-watty-purple underline">
          Voltar ao login
        </Link>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-watty-bg text-watty-ink">
      <aside className="flex w-[min(100%,16rem)] shrink-0 flex-col border-r border-watty-border bg-white/90 px-2 py-4 md:w-64">
        <div className="mb-4 flex justify-center px-2">
          <Image
            src="/watty_logosuperior.jpeg"
            alt="Watty"
            width={140}
            height={48}
            className="h-auto max-h-12 w-auto object-contain"
            priority
          />
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {nav.map((item) => {
            const on = activeNav === item.key;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-xl px-3 py-2.5 text-sm font-bold transition-colors ${
                  on
                    ? "border-2 border-watty-btn bg-[#F3E5F5] text-watty-purple"
                    : "border-2 border-transparent text-watty-purple hover:bg-watty-bg"
                }`}
              >
                <span className="mr-2">{item.emoji}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="mt-4 space-y-2 border-t border-watty-border pt-3 text-xs font-semibold text-slate-600">
          <label className="block px-1">Ano</label>
          <select
            className="w-full rounded-lg border border-watty-border bg-white px-2 py-2 text-sm font-bold text-watty-purple"
            value={ano}
            onChange={(e) => setAno(e.target.value)}
          >
            {LISTA_ANOS.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
          <label className="block px-1 pt-1">Disciplina</label>
          <select
            className="w-full rounded-lg border border-watty-border bg-white px-2 py-2 text-sm font-bold text-watty-purple"
            value={disciplina}
            onChange={(e) => setDisciplina(e.target.value)}
          >
            {disciplinasParaAno(ano).map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-watty-border bg-white/95 px-4 py-3">
          <div className="min-w-0 text-sm font-bold text-watty-purple">
            Olá, {profile.nome_display}
            <span className="ml-2 text-xs font-semibold text-slate-500">
              Nível {profile.nivel} · {profile.xp} XP · 🔥 {profile.streak} dia(s)
            </span>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <Link
              href="/perfil"
              className="rounded-lg border border-watty-border px-3 py-1.5 text-xs font-bold text-watty-purple hover:bg-watty-bg"
            >
              Perfil
            </Link>
            <button
              type="button"
              onClick={() => void logout()}
              className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-200"
            >
              Sair
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-auto p-4 md:p-6">
          <UiContextBridge ano={ano} disciplina={disciplina}>
            {children}
          </UiContextBridge>
        </main>

        <footer className="border-t border-watty-border bg-white/90 px-4 py-3 text-center text-xs text-slate-600">
          <a
            href={FOOTER_URL_LINKEDIN}
            target="_blank"
            rel="noreferrer"
            className="font-semibold text-watty-purple hover:underline"
          >
            LinkedIn
          </a>
          <span className="mx-2">·</span>
          <Link href="/quem-somos" className="font-semibold hover:underline">
            Quem somos
          </Link>
          <span className="mx-2">·</span>
          <Link href="/termos" className="font-semibold hover:underline">
            Termos
          </Link>
          <span className="mx-2">·</span>
          <a
            className="font-semibold hover:underline"
            href={`mailto:${FOOTER_EMAIL_AJUDA}`}
          >
            Ajuda
          </a>
        </footer>
      </div>
    </div>
  );
}

type WattyUiValue = { ano: string; disciplina: string };
const WattyUiContext = createContext<WattyUiValue | null>(null);

function UiContextBridge({
  ano,
  disciplina,
  children,
}: WattyUiValue & { children: React.ReactNode }) {
  const v = useMemo(() => ({ ano, disciplina }), [ano, disciplina]);
  return (
    <WattyUiContext.Provider value={v}>{children}</WattyUiContext.Provider>
  );
}

export function useWattyUi() {
  const c = useContext(WattyUiContext);
  if (!c) throw new Error("useWattyUi só dentro do AppShell");
  return c;
}
