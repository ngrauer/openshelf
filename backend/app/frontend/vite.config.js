import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Proxy every backend route in dev so we don't fight CORS.
      // Keep this list in sync with main.py router prefixes.
      "/auth": "http://localhost:8000",
      "/courses": "http://localhost:8000",
      "/textbooks": "http://localhost:8000",
      "/listings": "http://localhost:8000",
      "/matches": "http://localhost:8000",
      "/conversations": "http://localhost:8000",
      "/messages": "http://localhost:8000",
      "/reviews": "http://localhost:8000",
      "/notifications": "http://localhost:8000",
      "/chat": "http://localhost:8000",
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
