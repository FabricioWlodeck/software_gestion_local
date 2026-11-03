# Etapa 07: JavaScript vs TypeScript

Esta etapa acompaña al módulo [07, JavaScript vs TypeScript](../../explicaciones_didacticas/07_js_vs_ts.html). Son cuatro archivos chicos que se ejecutan con Node.js, sin navegador ni React.

| Archivo | Qué muestra |
|---|---|
| `01_fundamentos.js` | El JavaScript moderno que se usa en React: `const`, funciones flecha, `map`/`filter`, spread, `?.`, `async`/`await` |
| `02_carrito.js` | Un carrito con tres errores que JavaScript no avisa hasta ejecutarse (o nunca) |
| `03_carrito_con_errores.ts` | El mismo carrito con tipos: se ejecuta igual de mal, pero `tsc` encuentra los errores antes |
| `04_carrito_corregido.ts` | El carrito corregido siguiendo los avisos de TypeScript |

## Preparación (una vez)

Node.js 24 ejecuta archivos `.ts` directamente: borra los tipos y corre el resto. Para *verificar* los tipos hace falta el compilador de TypeScript, que se instala en esta carpeta:

```bash
npm install
```

Eso lee `package.json`, descarga TypeScript en `node_modules/` (que git ignora) y registra la versión exacta en `package-lock.json`.

## Cómo se ejecuta

```bash
node 01_fundamentos.js
```

```bash
node 02_carrito.js
```

```bash
node 03_carrito_con_errores.ts
```

```bash
npx tsc --noEmit
```

```bash
node 04_carrito_corregido.ts
```

`npx` ejecuta un programa instalado en `node_modules`. `tsc --noEmit` revisa los tipos de todos los `.ts` según `tsconfig.json` y no genera archivos. Los mismos comandos están como atajos en `package.json`: `npm run carrito-js`, `npm run verificar`, etc.

## Qué observar

1. `02_carrito.js` imprime `00.3502` como cantidad total y `NaN` como total, sin ningún error, y recién falla en la tercera parte.
2. `03_carrito_con_errores.ts` se ejecuta exactamente igual: los tipos no existen al ejecutar.
3. `npx tsc --noEmit` encuentra los tres errores (en cinco mensajes) sin ejecutar nada, y para la propiedad mal escrita sugiere el nombre correcto.
4. En `01_fundamentos.js`, `1450 * 1.1` da `1595.0000000000002`: es el error de punto flotante por el que el precio viaja como texto en la API.
