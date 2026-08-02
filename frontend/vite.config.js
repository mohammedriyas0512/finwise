import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend runs on :8000 in dev; proxy /api so cookies/headers are simple.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/exports': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 1500,
  },
})
