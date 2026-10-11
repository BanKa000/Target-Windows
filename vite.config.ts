import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { viteSingleFile } from "vite-plugin-singlefile";

// Плагин для удаления type="module" — чтобы файл работал при открытии через file://
function removeModuleType() {
  return {
    name: 'remove-module-type',
    transformIndexHtml(html: string) {
      return html
        .replace(/type="module"\s*/g, '')
        .replace(/crossorigin\s*/g, '');
    }
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), viteSingleFile(), removeModuleType()],
  base: './',
  build: {
    target: "es2015",
    assetsInlineLimit: 100000000,
    chunkSizeWarningLimit: 100000000,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
  },
  server: {
    host: "0.0.0.0",
    port: 3000,
    strictPort: true,
    hmr: {
      port: 3000,
    },
  },
});
