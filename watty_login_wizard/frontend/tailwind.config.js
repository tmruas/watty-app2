/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        /** Substituto oficial Duolingo quando não há Feather / DIN (Nunito). */
        sans: [
          "Nunito",
          "ui-sans-serif",
          "system-ui",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
      letterSpacing: {
        /** ~tracking -20 do Feather Bold (Duolingo Brand Guidelines). */
        feather: "-0.02em",
      },
      lineHeight: {
        /** Corpo ~140% DIN Next Rounded (guidelines Duolingo). */
        duobody: "1.4",
      },
      screens: {
        /** Telemóveis estreitos (acima do default `sm`) */
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
      maxWidth: {
        readable: "22rem",
      },
      minHeight: {
        /** Hero: chão mínimo + limite com svh (mobile / iframe) */
        "screen-safe":
          "max(18rem, min(32rem, 85svh))",
      },
      keyframes: {
        "watty-float": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-5px)" },
        },
        "watty-bolt": {
          "0%, 100%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.06)" },
        },
      },
      animation: {
        "watty-float": "watty-float 2.8s ease-in-out infinite",
        "watty-bolt": "watty-bolt 2.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
