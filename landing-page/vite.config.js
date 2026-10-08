import { defineConfig } from "vite";

// base relativa: el build funciona igual en la raíz de un dominio,
// en una subcarpeta o en GitHub Pages.
export default defineConfig({
  base: "./",
});
