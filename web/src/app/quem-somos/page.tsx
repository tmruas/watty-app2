import Link from "next/link";

export default function QuemSomosPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4 p-6">
      <Link href="/login" className="text-sm font-bold text-watty-purple hover:underline">
        ← Voltar
      </Link>
      <h1 className="text-2xl font-black text-watty-purple">Quem somos</h1>
      <p className="leading-relaxed text-slate-700">
        Bem-vindo ao Watty. Nós não somos mais um livro de exercícios aborrecido.
        Somos o teu explicador particular alimentado por Inteligência Artificial,
        disfarçado de videojogo.
      </p>
      <p className="leading-relaxed text-slate-700">
        Nascemos com uma missão clara: acabar com a &quot;seca&quot; de estudar para os
        Exames Nacionais. Aqui não há decorar à força. Há Boss Battles, treinos
        táticos e progresso gamificado.
      </p>
    </div>
  );
}
