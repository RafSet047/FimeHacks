import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import svgr from "vite-plugin-svgr";

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  base: command === "build" ? "/admin/" : "/",
  plugins: [
    react(),
    svgr({
      svgrOptions: {
        icon: true,
        // This will transform your SVG to a React component
        exportType: "named",
        namedExport: "ReactComponent",
      },
    }),
  ],
  server: {
    host: "0.0.0.0",
    port: 3001,
    proxy: {
      // Proxy API requests to the backend server
      "/process": {
        target: "http://localhost:8080",
        changeOrigin: true,
        secure: false,
      },
      "/search": {
        target: "http://localhost:8080",
        changeOrigin: true,
        secure: false,
      },
      "/health": {
        target: "http://localhost:8080",
        changeOrigin: true,
        secure: false,
      },
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
}));
