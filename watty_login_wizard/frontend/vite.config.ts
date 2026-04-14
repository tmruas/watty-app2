import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Caminhos relativos para o iframe do Streamlit servir assets corretamente
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "build",
    emptyOutDir: true,
  },
});
