import type { Metadata } from "next";
import { Fredoka, Nunito } from "next/font/google";
import "./globals.css";

const fredoka = Fredoka({
  subsets: ["latin"],
  variable: "--font-fredoka",
  weight: ["400", "600", "700"],
});

const nunito = Nunito({
  subsets: ["latin"],
  variable: "--font-nunito",
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "Watty | O teu Tutor Inteligente",
  description:
    "Perguntas, quizzes e resumos com IA — Watty, tutor para o ensino em Portugal.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt">
      <body
        className={`${fredoka.variable} ${nunito.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
