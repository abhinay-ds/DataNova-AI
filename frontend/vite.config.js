import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules")) {
            if (
              id.includes("react-dom") ||
              id.includes("react-router-dom") ||
              id.includes("/react/")
            ) {
              return "vendor-react";
            }
            if (id.includes("framer-motion") || id.includes("lucide-react")) {
              return "vendor-ui";
            }
            if (id.includes("react-markdown") || id.includes("remark-gfm") || id.includes("micromark")) {
              return "vendor-markdown";
            }
            return "vendor";
          }
        },
      },
    },
  },
});
