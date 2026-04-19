"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

export type WattyProfile = {
  email: string;
  nome_display: string;
  xp: number;
  nivel: number;
  streak: number;
  linha_bd: number;
  user_created_at: string | null;
};

type Ctx = {
  profile: WattyProfile | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  setLocalXpNivel: (xp: number, nivel: number) => void;
};

const WattyProfileContext = createContext<Ctx | null>(null);

export function WattyProfileProvider({ children }: { children: React.ReactNode }) {
  const [profile, setProfile] = useState<WattyProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/profile", { credentials: "include" });
      if (!res.ok) {
        const j = (await res.json().catch(() => ({}))) as { error?: string };
        throw new Error(j.error ?? `HTTP ${res.status}`);
      }
      const data = (await res.json()) as WattyProfile;
      setProfile(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao carregar perfil.");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const setLocalXpNivel = useCallback((xp: number, nivel: number) => {
    setProfile((p) => (p ? { ...p, xp, nivel } : p));
  }, []);

  const value = useMemo(
    () => ({ profile, loading, error, refresh, setLocalXpNivel }),
    [profile, loading, error, refresh, setLocalXpNivel]
  );

  return (
    <WattyProfileContext.Provider value={value}>
      {children}
    </WattyProfileContext.Provider>
  );
}

export function useWattyProfile() {
  const ctx = useContext(WattyProfileContext);
  if (!ctx) {
    throw new Error("useWattyProfile fora de WattyProfileProvider");
  }
  return ctx;
}
