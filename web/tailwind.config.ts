import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/context/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "var(--font-fredoka)",
          "var(--font-nunito)",
          "ui-sans-serif",
          "system-ui",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
      letterSpacing: {
        feather: "-0.02em",
      },
      lineHeight: {
        duobody: "1.4",
      },
      screens: {
        xs: "380px",
      },
      colors: {
        watty: {
          bg: "#E6DDF5",
          ink: "#311B52",
          purple: "#4A148C",
          btn: "#9C27B0",
          btnDark: "#7B1FA2",
          border: "#D1C4E9",
          accent: "#FFC107",
        },
      },
      boxShadow: {
        watty: "0px 6px 0px #7B1FA2",
        card: "0 4px 24px rgba(74, 20, 140, 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;
