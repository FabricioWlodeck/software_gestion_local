# Etapa 08: React + Vite

Esta etapa acompaña al módulo [08, React + Vite](../../explicaciones_didacticas/08_react_vite.html). Es la pantalla de caja de Punto Lácteo con datos de prueba, sin backend: lista de productos, carrito y total. El módulo 09 la conecta con la API de la etapa 06.

## Cómo se creó

El proyecto se generó con la plantilla oficial de Vite para React con TypeScript:

```bash
npm create vite@latest 08_react_vite -- --template react-ts
```

Después se borró la pantalla de demostración de la plantilla y se escribió la de Punto Lácteo.

## Estructura

```
08_react_vite/
├── index.html                 la única página: un <div id="root"> y el script de entrada
├── package.json               dependencias y comandos (dev, build, lint, preview)
├── vite.config.ts             configuración de Vite (el plugin de React)
├── tsconfig*.json             configuración de TypeScript
└── src/
    ├── main.tsx               punto de entrada: monta <App /> en #root
    ├── App.tsx                componente raíz: encabezado y pantalla
    ├── index.css              estilos globales
    ├── tipos.ts               interfaces compartidas (espejo de los schemas del backend)
    ├── datos/                 productos de prueba (el módulo 09 los cambia por la API)
    ├── utilidades/            funciones de formato, sin componentes
    └── features/ventas/       todo lo de la pantalla de ventas: componentes y estilos
        ├── PantallaVentas.tsx dueña del estado: productos y carrito
        ├── ListaProductos.tsx una tarjeta por producto
        ├── TarjetaProducto.tsx cantidad y botón Agregar (estado local)
        ├── Carrito.tsx        líneas, total y botón Cobrar
        └── ventas.css
```

## Cómo se ejecuta

Desde la carpeta de esta etapa, la primera vez:

```bash
npm install
```

Servidor de desarrollo en <http://localhost:5173>, con recarga al guardar:

```bash
npm run dev
```

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo con recarga en caliente |
| `npm run build` | Verifica tipos con `tsc` y genera la versión de producción en `dist/` |
| `npm run preview` | Sirve `dist/` para probar la versión de producción |
| `npm run lint` | Revisa el código con oxlint (errores comunes de React y TypeScript) |

## Qué observar

1. Con `npm run dev` abierto, agregá algo al carrito y después cambiá un texto en `Carrito.tsx` y guardá. La pantalla se actualiza sin recargar y el carrito conserva su contenido: es la recarga en caliente.
2. «1,5» leches muestra un error en la tarjeta, sin tocar el carrito: esa validación es local de la tarjeta.
3. El total del carrito coincide con el que calcula el backend ($7.275 para 0,350 kg de queso y 2 leches), pero es solo una estimación para mostrar. El que vale es el del backend.
