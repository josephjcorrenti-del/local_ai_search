import { defineConfig } from "vite";

export default defineConfig({
  base: "/search/",
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});
