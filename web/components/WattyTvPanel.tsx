"use client";

/**
 * Conteúdo de `web/src/app/(shell)/watty-tv/page.tsx` no commit `bcca015`.
 * O segundo vídeo existia só no commit seguinte (`7a102e6`); está em `public/media/wattyvid2.mp4`.
 */
const CARDS = [
  {
    title: "Como tirar o máximo do teu tutor Watty",
    video: "/media/wattyvid1.mp4",
    poster: "/watty3.png",
  },
  {
    title: "Dicas de revisão antes do teste intermédio",
    video: "/media/wattyvid2.mp4",
    poster: "/watty4.png",
  },
];

export function WattyTvPanel() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-black text-watty-purple">Watty TV</h1>
      <div className="grid gap-6 md:grid-cols-2">
        {CARDS.map((c) => (
          <article
            key={c.title}
            className="overflow-hidden rounded-2xl border border-watty-border bg-slate-900 shadow-lg"
          >
            <video
              controls
              playsInline
              preload="metadata"
              poster={c.poster}
              className="aspect-video w-full bg-black object-cover"
            >
              <source src={c.video} type="video/mp4" />
            </video>
            <p className="bg-white/95 px-3 py-2 text-sm font-bold text-watty-purple">{c.title}</p>
            <p className="px-3 pb-3 text-xs text-slate-500">
              Coloca os ficheiros .mp4 em{" "}
              <code className="rounded bg-slate-100 px-1">web/public/media/</code> se o vídeo não
              carregar.
            </p>
          </article>
        ))}
      </div>
    </div>
  );
}
