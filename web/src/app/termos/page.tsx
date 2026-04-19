import Link from "next/link";

export default function TermosPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4 p-6">
      <Link href="/login" className="text-sm font-bold text-watty-purple hover:underline">
        ← Voltar
      </Link>
      <h1 className="text-2xl font-black text-watty-purple">Termos e privacidade</h1>
      <h2 className="text-lg font-bold text-slate-800">Utilização do serviço</h2>
      <p className="text-sm leading-relaxed text-slate-700">
        Ao utilizares a aplicação Watty, comprometes-te a usar o serviço de forma
        responsável e de acordo com as leis aplicáveis. O conteúdo gerado por IA é
        informativo e pedagógico; não substitui orientação de professores, manuais
        oficiais nem aconselhamento profissional.
      </p>
      <h2 className="text-lg font-bold text-slate-800">Dados pessoais</h2>
      <p className="text-sm leading-relaxed text-slate-700">
        Tratamos o mínimo de dados necessários para autenticação (por exemplo, email
        via Supabase) e para o teu progresso na plataforma. Consulta a política do
        teu estabelecimento de ensino e o RGPD aplicável.
      </p>
      <p className="text-xs text-slate-500">
        Este texto é um modelo genérico. Deve ser revisto por aconselhamento jurídico
        antes de uso público.
      </p>
    </div>
  );
}
