import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Mantine + React pesan ~570 kB sin comprimir (~175 kB con gzip). Se usa en la red del local
    // y el navegador lo guarda en caché, así que se sube el aviso en vez de partir más el código.
    chunkSizeWarningLimit: 700,
  },
  server: {
    // Proxy de desarrollo: el navegador solo habla con Vite (5173) y Vite reenvía /api al backend.
    // En producción hace lo mismo nginx (ver nginx.conf). Así no hace falta CORS.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        rewrite: (ruta) => ruta.replace(/^\/api/, ''), // /api/productos → /productos
      },
    },
  },
})
