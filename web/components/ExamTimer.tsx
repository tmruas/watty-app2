"use client";

import { useEffect, useState } from "react";

const TOTAL_SEC = 100 * 60;

export function ExamTimer() {
  const [left, setLeft] = useState(TOTAL_SEC);

  useEffect(() => {
    const id = setInterval(() => {
      setLeft((t) => (t > 0 ? t - 1 : 0));
    }, 1000);
    return () => clearInterval(id);
  }, []);

  const m = Math.floor(left / 60);
  const s = left % 60;
  const label = `${m}:${s < 10 ? "0" : ""}${s}`;

  return (
    <div className="rounded-xl border-2 border-[#FF4B4B] bg-[#ffeaea] px-4 py-3 text-center font-sans text-2xl font-bold text-[#FF4B4B]">
      ⏱️ Tempo restante: <span>{label}</span>
    </div>
  );
}
