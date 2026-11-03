import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy de desarrollo: el navegador solo habla con Vite (localhost:5173), y Vite reenvía
    // todo lo que empieza con /api al backend de la etapa 06. Como para el navegador todo viene
    // del mismo origen, no hace falta configurar CORS. En el módulo 10, nginx hace este mismo trabajo.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        rewrite: (ruta) => ruta.replace(/^\/api/, ''), // /api/productos → /productos
      },
    },
  },
})
