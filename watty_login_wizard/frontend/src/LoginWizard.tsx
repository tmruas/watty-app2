import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Streamlit, type ComponentProps } from "streamlit-component-lib";

type Step = "hero" | "nome" | "idade" | "escola" | "loading";

const LOADING_MS = 1800;

const slide = {
  initial: { opacity: 0, x: 28 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -28 },
  transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] as const },
};

function OlaNome({ nome }: { nome: string }) {
  const n = nome.trim();
  if (!n) return null;
  return (
    <motion.p
      className="text-center text-2xl sm:text-3xl font-black text-watty-purple"
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

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [step, erro]);

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
    <div className="min-h-[560px] w-full max-w-lg mx-auto px-4 py-8 text-watty-ink">
      <AnimatePresence mode="wait">
        {step === "hero" && (
          <motion.section
            key="hero"
            className="flex flex-col items-center text-center gap-6"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.4 }}
          >
            <p className="text-5xl" aria-hidden>
              ⚡
            </p>
            <h1 className="text-3xl sm:text-4xl font-black text-watty-purple tracking-tight">
              Bem-vindo ao Watty!
            </h1>
            <p className="text-lg font-semibold text-watty-ink/90 max-w-md">
              O teu tutor inteligente 24/7.
            </p>
            <button
              type="button"
              disabled={disabled}
              onClick={avancarHero}
              className="mt-2 rounded-2xl bg-watty-btn px-8 py-3 text-white font-black uppercase tracking-wide text-sm shadow-watty border-2 border-watty-btnDark transition hover:bg-[#AB47BC] enabled:active:translate-y-1.5 enabled:active:shadow-none disabled:opacity-50"
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
            <p className="text-xl font-bold text-watty-purple text-center">
              Qual é o teu nome?
            </p>
            <input
              autoFocus
              disabled={disabled}
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && avancarNome()}
              placeholder="O teu nome"
              className="w-full rounded-2xl border-2 border-watty-border bg-white px-4 py-3.5 text-watty-purple font-semibold placeholder:text-watty-ink/40 focus:border-watty-accent focus:outline-none focus:ring-4 focus:ring-amber-200/50 disabled:opacity-50"
            />
            {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
            <div className="flex justify-end">
              <button
                type="button"
                disabled={disabled}
                onClick={avancarNome}
                className="rounded-2xl bg-watty-btn px-8 py-3 text-white font-black uppercase tracking-wide text-sm shadow-watty border-2 border-watty-btnDark transition hover:bg-[#AB47BC] enabled:active:translate-y-1.5 enabled:active:shadow-none disabled:opacity-50"
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
            <p className="text-xl font-bold text-watty-purple text-center">
              Qual é a tua idade?
            </p>
            <input
              autoFocus
              disabled={disabled}
              type="number"
              min={1}
              max={120}
              inputMode="numeric"
              value={idade}
              onChange={(e) => setIdade(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && avancarIdade()}
              placeholder="Ex: 12"
              className="w-full rounded-2xl border-2 border-watty-border bg-white px-4 py-3.5 text-watty-purple font-semibold placeholder:text-watty-ink/40 focus:border-watty-accent focus:outline-none focus:ring-4 focus:ring-amber-200/50 disabled:opacity-50"
            />
            {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
            <div className="flex justify-between gap-3">
              <button
                type="button"
                disabled={disabled}
                onClick={() => {
                  setErro(null);
                  setStep("nome");
                }}
                className="rounded-2xl border-2 border-watty-border bg-white px-5 py-3 font-bold text-watty-purple hover:bg-watty-bg disabled:opacity-50"
              >
                Voltar
              </button>
              <button
                type="button"
                disabled={disabled}
                onClick={avancarIdade}
                className="rounded-2xl bg-watty-btn px-8 py-3 text-white font-black uppercase tracking-wide text-sm shadow-watty border-2 border-watty-btnDark transition hover:bg-[#AB47BC] enabled:active:translate-y-1.5 enabled:active:shadow-none disabled:opacity-50"
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
            <p className="text-xl font-bold text-watty-purple text-center leading-snug">
              Qual é o nome da tua escola e turma?
            </p>
            <input
              autoFocus
              disabled={disabled}
              type="text"
              value={escolaTurma}
              onChange={(e) => setEscolaTurma(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && avancarEscola()}
              placeholder="Ex: Escola Secundária X — 8º B"
              className="w-full rounded-2xl border-2 border-watty-border bg-white px-4 py-3.5 text-watty-purple font-semibold placeholder:text-watty-ink/40 focus:border-watty-accent focus:outline-none focus:ring-4 focus:ring-amber-200/50 disabled:opacity-50"
            />
            {erro && <p className="text-sm font-semibold text-red-700">{erro}</p>}
            <div className="flex justify-between gap-3 flex-wrap">
              <button
                type="button"
                disabled={disabled}
                onClick={() => {
                  setErro(null);
                  setStep("idade");
                }}
                className="rounded-2xl border-2 border-watty-border bg-white px-5 py-3 font-bold text-watty-purple hover:bg-watty-bg disabled:opacity-50"
              >
                Voltar
              </button>
              <button
                type="button"
                disabled={disabled}
                onClick={avancarEscola}
                className="rounded-2xl bg-watty-btn px-6 py-3 text-white font-black uppercase tracking-wide text-sm shadow-watty border-2 border-watty-btnDark transition hover:bg-[#AB47BC] enabled:active:translate-y-1.5 enabled:active:shadow-none disabled:opacity-50"
              >
                Entrar no jogo 🚀
              </button>
            </div>
          </motion.div>
        )}

        {step === "loading" && (
          <motion.div
            key="loading"
            className="flex flex-col items-center justify-center gap-8 py-16"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <motion.p
              className="text-center text-2xl sm:text-3xl font-black text-watty-purple px-2"
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
            <p className="text-center text-lg font-bold text-watty-purple max-w-sm">
              Estamos a preparar o Watty para ti
            </p>
            <div className="watty-shimmer-bar h-3 w-48 rounded-full overflow-hidden bg-watty-border/60" />
          </motion.div>
        )}
      </AnimatePresence>

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
