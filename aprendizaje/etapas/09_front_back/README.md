# Etapa 09: frontend ↔ backend

Esta etapa acompaña al módulo [09, frontend ↔ backend](../../explicaciones_didacticas/09_front_back.html). Es la pantalla de caja de la etapa 08 conectada a la API de la etapa 06: inicio de sesión, productos reales, ventas que se guardan en MariaDB y un resumen que solo ve el rol dueño.

| Archivo nuevo o cambiado | Qué hace |
|---|---|
| `vite.config.ts` | Proxy de desarrollo: `/api/...` se reenvía a `http://127.0.0.1:8000/...` |
| `src/api/cliente.ts` | El único lugar que conoce URLs, headers y el token. Las pantallas llaman a `api.listarProductos()` |
| `src/tipos.ts` | Interfaces espejo de los schemas de la etapa 06 (`Producto`, `Venta`, `Usuario`, `Token`) |
| `src/features/auth/` | Contexto de sesión, `useSesion()` y la pantalla de inicio de sesión |
| `src/App.tsx` | Muestra el inicio de sesión o la caja según haya sesión |
| `src/features/ventas/PantallaVentas.tsx` | Carga productos de la API y cobra con `POST /ventas` |
| `src/features/ventas/ResumenVentas.tsx` | `GET /ventas`, visible solo para el rol dueño |

## Cómo se ejecuta

Hacen falta tres cosas corriendo:

1. El contenedor de MariaDB (`docker start pl-mariadb`).
2. El backend de la etapa 06, en una terminal, desde `etapas/06_seguridad` y con el entorno virtual activado:

```bash
fastapi dev app/main.py
```

3. El frontend, en otra terminal, desde esta carpeta (la primera vez, antes, `npm install`):

```bash
npm run dev
```

Después se abre <http://localhost:5173> y se inicia sesión con un usuario de prueba de la etapa 06 (por ejemplo, Bruno, empleado, o Ana, dueño).

## Qué observar

1. En las herramientas de desarrollo del navegador (F12, pestaña Red o *Network*), todas las peticiones van a `localhost:5173/api/...`, nunca a `127.0.0.1:8000`. El proxy de Vite las reenvía.
2. En la pestaña Aplicación (*Application*) → Local Storage aparece `punto-lacteo.token` después de iniciar sesión, y desaparece al cerrarla.
3. Una venta sin stock muestra el mensaje del backend (409) y el carrito queda como estaba para corregirlo.
4. Bruno no ve el resumen de ventas; Ana sí. Aunque Bruno enviara la petición a mano, el backend respondería 403.
5. Al recargar la página con una sesión abierta, la aplicación pregunta a `/auth/yo` de quién es el token guardado. Si el token venció o fue alterado, vuelve al inicio de sesión.
