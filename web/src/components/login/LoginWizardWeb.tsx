import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from "framer-motion";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

export type WattyLoginArgs = {
  supabase_url?: string;
  supabase_anon_key?: string;
  supabase_email_redirect_url?: string;
};

export type WattyAuthPayload = {
  access_token: string;
  refresh_token: string;
  nome_display: string;
};

type LoginWizardWebProps = {
  disabled?: boolean;
  args?: WattyLoginArgs;
  onAuthenticated: (payload: WattyAuthPayload) => void;
};

type Step =
  | "landing"
  | "register_email"
  | "register_nome"
  | "register_idade"
  | "register_escola"
  | "register_password"
  | "register_pending_confirm"
  | "login"
  | "loading";

const LOADING_MS = 1800;

function readOuterViewportHeight(): number {
  if (typeof window === "undefined") return 0;
  try {
    const topWin = window.top;
    if (topWin && topWin !== window && typeof topWin.innerHeight === "number") {
      return Math.ceil(topWin.innerHeight);
    }
  } catch {
    /* cross-origin */
  }
  try {
    const parentWin = window.parent;
    if (parentWin && parentWin !== window && typeof parentWin.innerHeight === "number") {
      return Math.ceil(parentWin.innerHeight);
    }
  } catch {
    /* cross-origin */
  }
  return 0;
}

const inputClass =
  "w-full min-h-[48px] rounded-2xl border-2 border-watty-border bg-white px-4 py-3 text-base text-watty-purple font-semibold placeholder:text-watty-ink/40 focus:border-watty-accent focus:outline-none focus:ring-4 focus:ring-amber-200/50 disabled:opacity-50";

const btnPrimary =
  "inline-flex min-h-[48px] min-w-[44px] touch-manipulation items-center justify-center rounded-2xl bg-watty-btn px-6 sm:px-8 py-3 text-white font-black uppercase tracking-wide text-sm shadow-watty border-2 border-watty-btnDark transition-all duration-200 ease-out hover:scale-[1.02] hover:bg-[#AB47BC] motion-reduce:hover:scale-100 enabled:active:translate-y-1.5 enabled:active:scale-[0.98] enabled:active:shadow-none disabled:opacity-50";

const btnSecondary =
  "inline-flex min-h-[48px] min-w-[44px] touch-manipulation items-center justify-center rounded-2xl border-2 border-watty-border bg-white px-5 py-3 font-bold text-watty-purple hover:bg-watty-bg disabled:opacity-50";

const cardPanel =
  "w-full min-w-0 overflow-visible rounded-2xl bg-white/95 p-5 pb-6 shadow-card ring-1 ring-watty-border/60 transition-shadow duration-300 ease-out motion-reduce:transition-none sm:rounded-3xl sm:p-8 sm:pb-8 sm:hover:shadow-[0_8px_32px_rgba(74,20,140,0.12)] motion-reduce:sm:hover:shadow-card";

function OlaNome({ nome }: { nome: string }) {
  const n = nome.trim();
  if (!n) return null;
  return (
    <motion.p
      className="max-w-full break-words px-1 text-center text-xl font-black text-watty-purple sm:text-2xl md:text-3xl"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      Olá, {n}!
    </motion.p>
  );
}

function isValidEmail(s: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.trim());
}

export default function LoginWizardWeb({
  disabled = false,
  args,
  onAuthenticated,
}: LoginWizardWebProps) {
  const wattyArgs = (args ?? {}) as WattyLoginArgs;
  const supabase_url = (wattyArgs.supabase_url ?? "").trim();
  const supabase_anon_key = (wattyArgs.supabase_anon_key ?? "").trim();
  const supabase_email_redirect_from_args = (
    wattyArgs.supabase_email_redirect_url ?? ""
  ).trim();

  const emailRedirectTo = useMemo(() => {
    const fromSecrets = supabase_email_redirect_from_args;
    if (fromSecrets) return fromSecrets;
    if (typeof window !== "undefined" && window.location?.origin) {
      return window.location.origin;
    }
    return "";
  }, [supabase_email_redirect_from_args]);

  const supabase = useMemo<SupabaseClient | null>(() => {
    if (!supabase_url || !supabase_anon_key) return null;
    return createClient(supabase_url, supabase_anon_key);
  }, [supabase_url, supabase_anon_key]);

  const [step, setStep] = useState<Step>("landing");
  const [email, setEmail] = useState("");
  const [nome, setNome] = useState("");
  const [idade, setIdade] = useState("");
  const [escolaTurma, setEscolaTurma] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [resendBusy, setResendBusy] = useState(false);
  const [resendInfo, setResendInfo] = useState<string | null>(null);
  const enviado = useRef(false);
  const [focusOnInputs, setFocusOnInputs] = useState(false);
  const pendingAuth = useRef<{
    access_token: string;
    refresh_token: string;
    nome_display: string;
  } | null>(null);

  const prefersReducedMotion = useReducedMotion();

  const slide = useMemo(
    () => ({
      initial: {
        opacity: 0,
        x: prefersReducedMotion ? 0 : 20,
      },
      animate: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: prefersReducedMotion ? 0 : -20 },
      transition: {
        duration: prefersReducedMotion ? 0.15 : 0.35,
        ease: [0.22, 1, 0.36, 1] as const,
      },
    }),
    [prefersReducedMotion]
  );

  useEffect(() => {
    setFocusOnInputs(
      typeof window !== "undefined" &&
        window.matchMedia("(hover: hover) and (pointer: fine)").matches
    );
  }, []);

  const shellRef = useRef<HTMLDivElement>(null);

  const bumpFrameHeight = useCallback(() => {
    const shell = shellRef.current;
    const root = document.getElementById("root");
    const docEl = document.documentElement;
    const body = document.body;

    const fromShell = shell
      ? Math.ceil(Math.max(shell.scrollHeight, shell.offsetHeight, shell.clientHeight))
      : 0;
    const fromRoot = root
      ? Math.ceil(Math.max(root.scrollHeight, root.offsetHeight))
      : 0;
    const fromDoc = Math.ceil(
      Math.max(docEl.scrollHeight, docEl.offsetHeight, body.scrollHeight, body.offsetHeight)
    );

    const vv =
      typeof window !== "undefined" && window.visualViewport?.height
        ? Math.ceil(window.visualViewport.height)
        : 0;
    const innerH = typeof window !== "undefined" ? Math.ceil(window.innerHeight) : 0;
    const outerH = readOuterViewportHeight();
    const viewFloor = Math.max(vv, innerH, outerH);

    Math.max(fromShell, fromRoot, fromDoc, viewFloor, 320);
  }, []);

  const publicAsset = useCallback((name: string) => `/${name}`, []);

  useLayoutEffect(() => {
    bumpFrameHeight();
    const id = requestAnimationFrame(() => {
      bumpFrameHeight();
      requestAnimationFrame(() => bumpFrameHeight());
    });
    const t = window.setTimeout(() => bumpFrameHeight(), 50);
    const t2 = window.setTimeout(() => bumpFrameHeight(), 200);
    return () => {
      cancelAnimationFrame(id);
      window.clearTimeout(t);
      window.clearTimeout(t2);
    };
  }, [bumpFrameHeight, step, erro, nome, email, busy, loginEmail, resendInfo]);

  useEffect(() => {
    const el = shellRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(() => bumpFrameHeight());
    ro.observe(el);
    bumpFrameHeight();
    return () => ro.disconnect();
  }, [bumpFrameHeight]);

  useEffect(() => {
    const onViewportChange = () => bumpFrameHeight();
    window.addEventListener("resize", onViewportChange);
    window.addEventListener("orientationchange", onViewportChange);
    window.addEventListener("scroll", onViewportChange, true);
    window.visualViewport?.addEventListener("resize", onViewportChange);
    window.visualViewport?.addEventListener("scroll", onViewportChange);
    return () => {
      window.removeEventListener("resize", onViewportChange);
      window.removeEventListener("orientationchange", onViewportChange);
      window.removeEventListener("scroll", onViewportChange, true);
      window.visualViewport?.removeEventListener("resize", onViewportChange);
      window.visualViewport?.removeEventListener("scroll", onViewportChange);
    };
  }, [bumpFrameHeight]);

  useEffect(() => {
    if (step !== "loading" || !pendingAuth.current || enviado.current) return;

    const t = window.setTimeout(() => {
      if (enviado.current || !pendingAuth.current) return;
      enviado.current = true;
      onAuthenticated({ ...pendingAuth.current });
    }, LOADING_MS);

    return () => window.clearTimeout(t);
  }, [step, onAuthenticated]);

  const goToLoadingWithAuth = (
    access_token: string,
    nome_display: string,
    refresh_token: string
  ) => {
    pendingAuth.current = {
      access_token,
      refresh_token,
      nome_display: nome_display.trim(),
    };
    enviado.current = false;
    setErro(null);
    setStep("loading");
  };

  const handleLogin = async () => {
    if (!supabase) {
      setErro("Supabase não configurado.");
      return;
    }
    setErro(null);
    if (!loginEmail.trim() || !loginPassword) {
      setErro("Preenche o email e a palavra-passe.");
      return;
    }
    setBusy(true);
    const { data, error } = await supabase.auth.signInWithPassword({
      email: loginEmail.trim().toLowerCase(),
      password: loginPassword,
    });
    setBusy(false);
    if (error || !data.session) {
      setErro(error?.message ?? "Não foi possível entrar. Verifica as credenciais.");
      return;
    }
    const meta = (data.user?.user_metadata ?? {}) as Record<string, unknown>;
    const display =
      (typeof meta.nome_display === "string" && meta.nome_display.trim()) ||
      (typeof meta.nome === "string" && meta.nome.trim()) ||
      loginEmail.split("@")[0] ||
      "Aluno";
    goToLoadingWithAuth(
      data.session.access_token,
      display,
      data.session.refresh_token
    );
  };

  const handleRegisterFinish = async () => {
    if (!supabase) {
      setErro("Supabase não configurado.");
      return;
    }
    setErro(null);
    const pw = regPassword.trim();
    if (pw.length < 6) {
      setErro("A palavra-passe deve ter pelo menos 6 caracteres.");
      return;
    }
    setBusy(true);
    const { data, error } = await supabase.auth.signUp({
      email: email.trim().toLowerCase(),
      password: pw,
      options: {
        ...(emailRedirectTo ? { emailRedirectTo } : {}),
        data: {
          nome_display: nome.trim(),
          nome: nome.trim(),
          idade: idade.trim(),
          escola_turma: escolaTurma.trim(),
        },
      },
    });
    setBusy(false);
    if (error) {
      setErro(error.message);
      return;
    }
    if (data.session) {
      goToLoadingWithAuth(
        data.session.access_token,
        nome.trim(),
        data.session.refresh_token
      );
      return;
    }
    if (data.user) {
      setResendInfo(null);
      setErro(null);
      setStep("register_pending_confirm");
      return;
    }
    setErro(
      "A conta pode não ter sido criada. Tenta de novo ou verifica as definições de Auth no painel Supabase."
    );
  };

  const handleResendConfirmation = async () => {
    if (!supabase) return;
    setResendInfo(null);
    setResendBusy(true);
    const { error } = await supabase.auth.resend({
      type: "signup",
      email: email.trim().toLowerCase(),
      options: emailRedirectTo ? { emailRedirectTo } : undefined,
    });
    setResendBusy(false);
    if (error) {
      setResendInfo(error.message);
      return;
    }
    setResendInfo(
      "Pedido enviado. Verifica a caixa de entrada e a pasta de spam. O email é enviado pelo Supabase (Auth), não depende de tabelas na base de dados."
    );
  };

  const avancarEmail = () => {
    if (!isValidEmail(email)) {
      setErro("Indica um email válido.");
      return;
    }
    setErro(null);
    setStep("register_nome");
  };

  const avancarNome = () => {
    if (!nome.trim()) {
      setErro("Escreve o teu nome para continuares.");
      return;
    }
    setErro(null);
    setStep("register_idade");
  };

  const avancarIdade = () => {
    const n = idade.trim();
    if (!n) {
      setErro("Indica a tua idade.");
      return;
    }
    if (!/^\d+$/.test(n) || Number(n) < 1 || Number(n) > 120) {
      setErro("Indica uma idade válida (número entre 1 e 120).");
      return;
    }
    setErro(null);
    setStep("register_escola");
  };

  const avancarEscola = () => {
    if (!escolaTurma.trim()) {
      setErro("Escreve o nome da escola e da turma.");
      return;
    }
    setErro(null);
    setStep("register_password");
  };

  const configMissing = !supabase;

  return (
    <div
      ref={shellRef}
      className="box-border flex min-h-full min-h-screen min-h-[100svh] min-h-[100dvh] w-full min-w-0 max-w-full flex-1 flex-col items-stretch bg-white text-watty-ink"
    >
      {configMissing && (
        <div className="mx-auto max-w-lg px-4 py-6 text-center text-sm font-semibold text-red-700">
          Falta configurar o Supabase (URL e chave anon nas variáveis de ambiente).
        </div>
      )}

      {step === "landing" && (
        <div className="flex w-full flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-slate-100 px-4 py-4 sm:px-8">
            <span className="text-xl font-black tracking-tight text-watty-purple">
              watty
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Português
            </span>
          </header>

          <section className="mx-auto grid w-full max-w-6xl flex-1 items-center gap-10 px-4 py-10 md:grid-cols-2 md:gap-12 md:py-16">
            <div className="flex justify-center md:justify-end">
              <img
                src={publicAsset("WATTY.jpg")}
                alt="Logótipo Watty"
                className="mx-auto h-auto w-full max-w-[min(100%,18rem)] object-contain drop-shadow-[0_6px_24px_rgba(74,20,140,0.12)] sm:max-w-xs md:mx-0"
                onLoad={bumpFrameHeight}
              />
            </div>
            <div className="flex flex-col items-center gap-6 text-center md:items-start md:text-left">
              <h1 className="max-w-xl text-balance text-3xl font-black leading-tight tracking-tight text-slate-800 sm:text-4xl md:text-[2.35rem]">
                O jeito divertido e eficaz de aprender com o teu tutor inteligente.
              </h1>
              <p className="max-w-md text-lg font-semibold text-slate-600">
                Perguntas, quizzes e resumos ao teu ritmo — com o Watty ao teu lado.
              </p>
              <div className="mt-2 flex w-full max-w-md flex-col gap-3 sm:flex-row sm:justify-start">
                <button
                  type="button"
                  disabled={disabled || configMissing}
                  onClick={() => {
                    setErro(null);
                    setStep("register_email");
                  }}
                  className={`${btnPrimary} w-full sm:w-auto`}
                >
                  Comece agora
                </button>
                <button
                  type="button"
                  disabled={disabled || configMissing}
                  onClick={() => {
                    setErro(null);
                    setStep("login");
                  }}
                  className={`${btnSecondary} w-full border-slate-200 sm:w-auto`}
                >
                  Já tenho uma conta
                </button>
              </div>
            </div>
          </section>

          <div className="border-t border-slate-100 bg-slate-50/80">
            <div className="mx-auto max-w-6xl space-y-0 px-4 py-16 sm:px-8">
              <MarketingBlock
                title="Aprende ao teu ritmo"
                body="O Watty adapta-se ao teu ano e disciplina, para praticares o que realmente importa na escola."
                imageSrc={publicAsset("watty1.png")}
                imageAlt="Watty a estudar ao teu ritmo"
                imageLeft
                onImageLoad={bumpFrameHeight}
              />
              <MarketingBlock
                title="Chat socrático com IA"
                body="Faz perguntas, recebe pistas em vez de respostas prontas à laia, e fixa melhor o conteúdo."
                imageSrc={publicAsset("watty2.png")}
                imageAlt="Watty no diálogo com IA"
                imageLeft={false}
                onImageLoad={bumpFrameHeight}
              />
              <MarketingBlock
                title="Treina com quizzes"
                body="Consolida matéria com desafios rápidos e feedback imediato — estilo jogo, foco em progresso."
                imageSrc={publicAsset("watty3.png")}
                imageAlt="Watty a treinar com quizzes"
                imageLeft
                onImageLoad={bumpFrameHeight}
              />
              <MarketingBlock
                title="O teu progresso na nuvem"
                body="XP, nível e streak guardados para continuares de onde paraste, em qualquer sessão."
                imageSrc={publicAsset("watty4.png")}
                imageAlt="Logótipo Watty"
                imageLeft={false}
                onImageLoad={bumpFrameHeight}
              />
            </div>
          </div>
        </div>
      )}

      {step !== "landing" && (
        <div className="flex flex-1 flex-col items-center justify-center px-[max(1rem,env(safe-area-inset-left))] py-8 pr-[max(1rem,env(safe-area-inset-right))]">
          <div className="w-full min-w-0 max-w-full sm:max-w-lg">
            <div className={cardPanel}>
              <AnimatePresence mode="wait">
                {step === "register_email" && (
                  <motion.div key="register_email" {...slide} className="space-y-6">
                    <p className="text-center text-4xl" aria-hidden>
                      ✉️
                    </p>
                    <p className="text-center text-lg font-bold text-watty-purple sm:text-xl">
                      Qual é o teu email?
                    </p>
                    <p className="text-center text-sm font-medium text-watty-ink/80">
                      Vamos usá-lo para guardares o teu progresso com segurança.
                    </p>
                    <input
                      autoFocus={focusOnInputs}
                      autoComplete="email"
                      enterKeyHint="next"
                      disabled={disabled}
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && avancarEmail()}
                      placeholder="nome@escola.pt"
                      className={inputClass}
                    />
                    {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => {
                          setErro(null);
                          setStep("landing");
                        }}
                        className={`${btnSecondary} w-full sm:w-auto`}
                      >
                        Voltar
                      </button>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={avancarEmail}
                        className={`${btnPrimary} w-full sm:w-auto`}
                      >
                        Seguinte
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === "register_nome" && (
                  <motion.div key="register_nome" {...slide} className="space-y-6">
                    <p className="text-center text-4xl" aria-hidden>
                      👋
                    </p>
                    <OlaNome nome={nome} />
                    <p className="text-center text-lg font-bold text-watty-purple sm:text-xl">
                      Qual é o teu nome?
                    </p>
                    <input
                      autoFocus={focusOnInputs}
                      autoComplete="name"
                      enterKeyHint="next"
                      disabled={disabled}
                      type="text"
                      value={nome}
                      onChange={(e) => setNome(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && avancarNome()}
                      placeholder="O teu nome"
                      className={inputClass}
                    />
                    {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => {
                          setErro(null);
                          setStep("register_email");
                        }}
                        className={`${btnSecondary} w-full sm:w-auto`}
                      >
                        Voltar
                      </button>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={avancarNome}
                        className={`${btnPrimary} w-full sm:w-auto`}
                      >
                        Seguinte
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === "register_idade" && (
                  <motion.div key="register_idade" {...slide} className="space-y-6">
                    <p className="text-center text-4xl" aria-hidden>
                      🎂
                    </p>
                    <OlaNome nome={nome} />
                    <p className="text-center text-lg font-bold text-watty-purple sm:text-xl">
                      Qual é a tua idade?
                    </p>
                    <input
                      autoFocus={focusOnInputs}
                      autoComplete="off"
                      enterKeyHint="next"
                      disabled={disabled}
                      type="number"
                      min={1}
                      max={120}
                      inputMode="numeric"
                      value={idade}
                      onChange={(e) => setIdade(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && avancarIdade()}
                      placeholder="Ex: 12"
                      className={inputClass}
                    />
                    {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => {
                          setErro(null);
                          setStep("register_nome");
                        }}
                        className={`${btnSecondary} w-full sm:w-auto`}
                      >
                        Voltar
                      </button>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={avancarIdade}
                        className={`${btnPrimary} w-full sm:w-auto`}
                      >
                        Seguinte
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === "register_escola" && (
                  <motion.div key="register_escola" {...slide} className="space-y-6">
                    <p className="text-center text-4xl" aria-hidden>
                      🏫
                    </p>
                    <OlaNome nome={nome} />
                    <p className="text-center text-lg font-bold leading-snug text-watty-purple sm:text-xl">
                      Qual é o nome da tua escola e turma?
                    </p>
                    <input
                      autoFocus={focusOnInputs}
                      autoComplete="organization"
                      enterKeyHint="done"
                      disabled={disabled}
                      type="text"
                      value={escolaTurma}
                      onChange={(e) => setEscolaTurma(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && avancarEscola()}
                      placeholder="Ex: Escola Secundária X — 8º B"
                      className={inputClass}
                    />
                    {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => {
                          setErro(null);
                          setStep("register_idade");
                        }}
                        className={`${btnSecondary} w-full sm:w-auto`}
                      >
                        Voltar
                      </button>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={avancarEscola}
                        className={`${btnPrimary} w-full px-4 sm:w-auto sm:px-6`}
                      >
                        Seguinte
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === "register_password" && (
                  <motion.div key="register_password" {...slide} className="space-y-6">
                    <p className="text-center text-4xl" aria-hidden>
                      🔐
                    </p>
                    <OlaNome nome={nome} />
                    <p className="text-center text-lg font-bold text-watty-purple sm:text-xl">
                      Cria a tua palavra-passe
                    </p>
                    <p className="text-center text-sm font-medium text-watty-ink/80">
                      Mínimo de 6 caracteres (regra típica do Supabase).
                    </p>
                    <input
                      autoFocus={focusOnInputs}
                      autoComplete="new-password"
                      enterKeyHint="done"
                      disabled={disabled || busy}
                      type="password"
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && void handleRegisterFinish()}
                      placeholder="Palavra-passe"
                      className={inputClass}
                    />
                    {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                      <button
                        type="button"
                        disabled={disabled || busy}
                        onClick={() => {
                          setErro(null);
                          setStep("register_escola");
                        }}
                        className={`${btnSecondary} w-full sm:w-auto`}
                      >
                        Voltar
                      </button>
                      <button
                        type="button"
                        disabled={disabled || busy}
                        onClick={() => void handleRegisterFinish()}
                        className={`${btnPrimary} w-full sm:w-auto`}
                      >
                        {busy ? "A criar conta…" : "Criar conta"}
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === "register_pending_confirm" && (
                  <motion.div
                    key="register_pending_confirm"
                    {...slide}
                    className="space-y-5"
                  >
                    <p className="text-center text-4xl" aria-hidden>
                      📬
                    </p>
                    <p className="text-center text-lg font-black text-watty-purple sm:text-xl">
                      Falta confirmar o email
                    </p>
                    <p className="text-center text-sm font-semibold leading-relaxed text-watty-ink/85">
                      O Supabase envia o link de confirmação automaticamente (não precisas de criar
                      tabelas para isso). Se não vês nada, verifica o spam e confirma no painel que o
                      URL de redirecionamento inclui{" "}
                      <span className="break-all font-mono text-xs text-watty-purple">
                        {emailRedirectTo || "(origem desta página)"}
                      </span>
                      .
                    </p>
                    <div className="rounded-2xl border-2 border-amber-200/90 bg-amber-50/90 p-4 text-left text-xs font-semibold leading-relaxed text-amber-950/90">
                      <strong className="block text-sm text-amber-950">Desenvolvimento local</strong>
                      No Supabase: Authentication → Providers → Email → desativa{" "}
                      <em>Confirm email</em>. Volta a criar conta ou confirma o utilizador em
                      Authentication → Users. Assim recebes sessão logo após o registo sem depender
                      do correio.
                    </div>
                    <p className="text-center text-xs font-semibold text-watty-ink/70">
                      Conta: <span className="break-all">{email.trim().toLowerCase()}</span>
                    </p>
                    {resendInfo && (
                      <p className="rounded-xl bg-slate-50 px-3 py-2 text-center text-sm font-semibold text-slate-800">
                        {resendInfo}
                      </p>
                    )}
                    <div className="flex flex-col gap-3">
                      <button
                        type="button"
                        disabled={disabled || resendBusy}
                        onClick={() => void handleResendConfirmation()}
                        className={`${btnPrimary} w-full`}
                      >
                        {resendBusy ? "A enviar…" : "Reenviar email de confirmação"}
                      </button>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => {
                          setResendInfo(null);
                          setLoginEmail(email.trim().toLowerCase());
                          setLoginPassword("");
                          setStep("login");
                        }}
                        className={`${btnSecondary} w-full`}
                      >
                        Já confirmei — ir para entrar
                      </button>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => {
                          setResendInfo(null);
                          setStep("landing");
                        }}
                        className={`${btnSecondary} w-full border-slate-200 text-sm`}
                      >
                        Voltar ao início
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === "login" && (
                  <motion.div key="login" {...slide} className="space-y-6">
                    <p className="text-center text-4xl" aria-hidden>
                      ⚡
                    </p>
                    <p className="text-center text-lg font-bold text-watty-purple sm:text-xl">
                      Entrar
                    </p>
                    <input
                      autoFocus={focusOnInputs}
                      autoComplete="email"
                      enterKeyHint="next"
                      disabled={disabled || busy}
                      type="email"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      placeholder="Email"
                      className={inputClass}
                    />
                    <input
                      autoComplete="current-password"
                      enterKeyHint="go"
                      disabled={disabled || busy}
                      type="password"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && void handleLogin()}
                      placeholder="Palavra-passe"
                      className={inputClass}
                    />
                    {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                      <button
                        type="button"
                        disabled={disabled || busy}
                        onClick={() => {
                          setErro(null);
                          setLoginPassword("");
                          setStep("landing");
                        }}
                        className={`${btnSecondary} w-full sm:w-auto`}
                      >
                        Voltar
                      </button>
                      <button
                        type="button"
                        disabled={disabled || busy}
                        onClick={() => void handleLogin()}
                        className={`${btnPrimary} w-full sm:w-auto`}
                      >
                        {busy ? "A entrar…" : "Entrar"}
                      </button>
                    </div>
                  </motion.div>
                )}

                {step === "loading" && (
                  <motion.div
                    key="loading"
                    className="flex flex-col items-center justify-center gap-6 py-10 sm:gap-8 sm:py-16"
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4 }}
                  >
                    <motion.p
                      className="max-w-[min(100%,24rem)] break-words px-2 text-center text-xl font-black text-watty-purple sm:text-2xl md:text-3xl"
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.35 }}
                    >
                      Bem-vindo, {nome.trim() || loginEmail.split("@")[0] || "aluno"}!
                    </motion.p>
                    <div
                      className="h-14 w-14 animate-spin rounded-full border-4 border-watty-border border-t-watty-btn"
                      role="status"
                      aria-label="A carregar"
                    />
                    <p className="max-w-sm text-center text-base font-bold text-watty-purple sm:text-lg">
                      Estamos a preparar o Watty para ti
                    </p>
                    <div className="watty-shimmer-bar h-3 w-48 max-w-[90vw] overflow-hidden rounded-full bg-watty-border/60" />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes watty-shimmer-bar {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .watty-shimmer-bar::after {
          content: "";
          display: block;
          height: 100%;
          width: 40%;
          background: linear-gradient(90deg, transparent, rgba(156, 39, 176, 0.35), transparent);
          animation: watty-shimmer-bar 1.2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}

function MarketingBlock({
  title,
  body,
  imageSrc,
  imageAlt,
  imageLeft,
  onImageLoad,
}: {
  title: string;
  body: string;
  imageSrc: string;
  imageAlt: string;
  imageLeft: boolean;
  onImageLoad?: () => void;
}) {
  const textBlock = (
    <div
      className={`flex min-w-0 flex-1 flex-col gap-2 ${
        imageLeft
          ? "items-center text-center md:items-end md:text-right"
          : "items-center text-center md:items-start md:text-left"
      }`}
    >
      <h2 className="text-xl font-black text-watty-purple sm:text-2xl">{title}</h2>
      <p className="mt-1 max-w-prose text-base font-medium leading-relaxed text-slate-600">
        {body}
      </p>
    </div>
  );

  const imageBlock = (
    <div
      className={`flex shrink-0 justify-center ${
        imageLeft ? "md:justify-start" : "md:justify-end"
      }`}
    >
      <img
        src={imageSrc}
        alt={imageAlt}
        className="h-auto w-full max-w-[min(100%,17.5rem)] object-contain sm:max-w-xs md:max-w-sm"
        onLoad={onImageLoad}
      />
    </div>
  );

  return (
    <div
      className={`flex flex-col gap-8 border-b border-slate-200 py-12 last:border-b-0 md:flex-row md:items-center md:gap-12 lg:gap-16 ${
        imageLeft ? "" : "flex-col-reverse md:flex-row-reverse"
      }`}
    >
      {imageBlock}
      {textBlock}
    </div>
  );
}
