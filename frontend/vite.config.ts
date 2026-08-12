import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The frontend is always served from the same origin as the API: by Vite's dev
// server here (proxying /api to uvicorn), by FastAPI in production.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET ?? "http://localhost:8000",
        changeOrigin: false,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    rollupOptions: {
      output: {
        // Recharts is by far the heaviest dependency and changes rarely, so it
        // gets its own long-lived chunk.
        manualChunks: {
          charts: ["recharts"],
          vendor: ["react", "react-dom", "react-router-dom", "axios"],
        },
      },
    },
  },
});
