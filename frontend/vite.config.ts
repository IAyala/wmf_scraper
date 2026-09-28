import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The frontend is always served from the same origin as the API: by Vite's dev
// server here (proxying /api to uvicorn), by FastAPI in production.
export default defineConfig({
  plugins: [react()],
  server: {
    // Listen on every interface, not just loopback. Inside a devcontainer the
    // default ("localhost") resolves to ::1 only, so the port forwarding, which
    // connects over IPv4, finds nothing and the browser shows a blank page.
    host: true,
    port: 3000,
    proxy: {
      "/api": {
        // 127.0.0.1 rather than localhost: uvicorn binds IPv4, and resolving
        // localhost to ::1 first would make the proxy miss it.
        target: process.env.VITE_API_TARGET ?? "http://127.0.0.1:8000",
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
