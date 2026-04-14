/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
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
      },
    },
  },
  plugins: [],
};
