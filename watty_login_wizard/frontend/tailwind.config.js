/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
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
    },
  },
  plugins: [],
};
