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
import { Streamlit, type ComponentProps } from "streamlit-component-lib";

type Step = "hero" | "nome" | "idade" | "escola" | "loading";

const LOADING_MS = 1800;

/** 16px+ evita zoom automático no foco (iOS Safari); altura mínima para toque. */
const inputClass =
  "w-full min-h-[48px] rounded-2xl border-2 border-watty-border bg-white px-4 py-3 text-base text-watty-purple font-semibold placeholder:text-watty-ink/40 focus:border-watty-accent focus:outline-none focus:ring-4 focus:ring-amber-200/50 disabled:opacity-50";

const btnPrimary =
  "inline-flex min-h-[48px] min-w-[44px] touch-manipulation items-center justify-center rounded-2xl bg-watty-btn px-6 sm:px-8 py-3 text-white font-black uppercase tracking-wide text-sm shadow-watty border-2 border-watty-btnDark transition hover:bg-[#AB47BC] enabled:active:translate-y-1.5 enabled:active:shadow-none disabled:opacity-50";

const btnSecondary =
  "inline-flex min-h-[48px] min-w-[44px] touch-manipulation items-center justify-center rounded-2xl border-2 border-watty-border bg-white px-5 py-3 font-bold text-watty-purple hover:bg-watty-bg disabled:opacity-50";

/** Cartão branco: legível em qualquer largura; sombra suave definida no tailwind.config */
const cardPanel =
  "w-full min-w-0 overflow-visible rounded-2xl bg-white/95 p-5 pb-6 shadow-card ring-1 ring-watty-border/60 sm:rounded-3xl sm:p-8 sm:pb-8";

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

export default function LoginWizard({ disabled }: ComponentProps) {
  const [step, setStep] = useState<Step>("hero");
  const [nome, setNome] = useState("");
  const [idade, setIdade] = useState("");
  const [escolaTurma, setEscolaTurma] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const enviado = useRef(false);
  const [focusOnInputs, setFocusOnInputs] = useState(false);

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

  /**
   * Streamlit usa document.body.scrollHeight por omissão — com min-height no body isso falha.
   * Medimos o contentor real e o maior valor possível para o iframe expandir com o conteúdo (mobile).
   */
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

    const h = Math.max(fromShell, fromRoot, fromDoc, 320);
    Streamlit.setFrameHeight(h);
  }, []);

  /** Após pintar o DOM: iframe acompanha logo o conteúdo (evita cortar o botão no mobile). */
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
  }, [bumpFrameHeight, step, erro, nome]);

  useEffect(() => {
    const el = shellRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(() => bumpFrameHeight());
    ro.observe(el);
    bumpFrameHeight();
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const onViewportChange = () => bumpFrameHeight();
    window.addEventListener("resize", onViewportChange);
    window.addEventListener("orientationchange", onViewportChange);
    window.visualViewport?.addEventListener("resize", onViewportChange);
    window.visualViewport?.addEventListener("scroll", onViewportChange);
    return () => {
      window.removeEventListener("resize", onViewportChange);
      window.removeEventListener("orientationchange", onViewportChange);
      window.visualViewport?.removeEventListener("resize", onViewportChange);
      window.visualViewport?.removeEventListener("scroll", onViewportChange);
    };
  }, []);

  useEffect(() => {
    if (step !== "loading" || enviado.current) return;

    const t = window.setTimeout(() => {
      if (enviado.current) return;
      enviado.current = true;
      Streamlit.setComponentValue({
        nome: nome.trim(),
        idade: idade.trim(),
        escola_turma: escolaTurma.trim(),
      });
    }, LOADING_MS);

    return () => window.clearTimeout(t);
  }, [step, nome, idade, escolaTurma]);

  const avancarHero = () => setStep("nome");

  const avancarNome = () => {
    if (!nome.trim()) {
      setErro("Escreve o teu nome para continuares.");
      return;
    }
    setErro(null);
    setStep("idade");
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
    setStep("escola");
  };

  const avancarEscola = () => {
    if (!escolaTurma.trim()) {
      setErro("Escreve o nome da escola e da turma.");
      return;
    }
    setErro(null);
    setStep("loading");
  };

  return (
    <div
      ref={shellRef}
      className="mx-auto box-border flex w-full min-w-0 max-w-full flex-col px-[max(1rem,env(safe-area-inset-left))] pb-[max(1.25rem,env(safe-area-inset-bottom))] pt-[max(0.5rem,env(safe-area-inset-top))] pr-[max(1rem,env(safe-area-inset-right))] text-watty-ink sm:max-w-lg"
    >
      <div className="w-full py-1 sm:py-4">
        <div className={cardPanel}>
          <AnimatePresence mode="wait">
            {step === "hero" && (
              <motion.section
                key="hero"
                className="flex flex-col items-center gap-4 text-center sm:min-h-0 sm:gap-6"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                transition={{ duration: 0.4 }}
              >
                <p className="text-4xl xs:text-5xl" aria-hidden>
                  ⚡
                </p>
                <h1 className="w-full max-w-full text-balance text-2xl font-black leading-tight tracking-tight text-watty-purple xs:text-3xl sm:text-3xl md:text-4xl">
                  Bem-vindo ao Watty!
                </h1>
                <p className="max-w-md leading-snug text-base font-semibold text-watty-ink/90 sm:text-lg">
                  O teu tutor inteligente 24/7.
                </p>
                <button
                  type="button"
                  disabled={disabled}
                  onClick={avancarHero}
                  className={`${btnPrimary} mt-2 w-full max-w-xs sm:mt-2 sm:w-auto`}
                >
                  Começar
                </button>
              </motion.section>
            )}

        {step === "nome" && (
          <motion.div key="nome" {...slide} className="space-y-6">
            <p className="text-4xl text-center" aria-hidden>
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
            <div className="flex justify-stretch sm:justify-end">
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

        {step === "idade" && (
          <motion.div key="idade" {...slide} className="space-y-6">
            <p className="text-4xl text-center" aria-hidden>
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
                  setStep("nome");
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

        {step === "escola" && (
          <motion.div key="escola" {...slide} className="space-y-6">
            <p className="text-4xl text-center" aria-hidden>
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
                  setStep("idade");
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
                Entrar no jogo 🚀
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
                  Bem-vindo, {nome.trim()}!
                </motion.p>
                <div
                  className="h-14 w-14 rounded-full border-4 border-watty-border border-t-watty-btn animate-spin"
                  role="status"
                  aria-label="A carregar"
                />
                <p className="max-w-sm text-center text-base font-bold text-watty-purple sm:text-lg">
                  Estamos a preparar o Watty para ti
                </p>
                <div className="watty-shimmer-bar h-3 w-48 max-w-[90vw] rounded-full overflow-hidden bg-watty-border/60" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

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
