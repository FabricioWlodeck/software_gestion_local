# Aprendizaje: cómo se conecta un sistema web con FastAPI, MariaDB y React

Este material sirve para entender cada pieza del sistema de Punto Lácteo antes de diseñarlo. En lugar de leer documentación suelta, se construye un mini Punto Lácteo reducido a tres entidades (productos, ventas y usuarios). Cada módulo agrega una sola pieza sobre el anterior.

El mini proyecto no es la base del sistema real. El MVP (*Minimum Viable Product* o Producto Mínimo Viable) se escribe desde cero aplicando lo aprendido. Este material se conserva como referencia.

## Cómo se estudia cada módulo

1. Abrir [`explicaciones_didacticas/index.html`](explicaciones_didacticas/index.html) con doble clic. Se abre en el navegador y no necesita internet.
2. Leer el módulo en orden. Todos tienen las mismas ocho secciones: problema, concepto, código mínimo, cómo se conecta, animación, errores comunes, ejercicios y documentación oficial.
3. Recorrer la animación con los botones o con las flechas del teclado.
4. Ejecutar la etapa de código correspondiente siguiendo su `README.md`.
5. Resolver los ejercicios antes de abrir las respuestas.

Cada módulo está pensado para estudiarse en 1 a 1,5 h.

## Temario

| # | Módulo | Pregunta que responde | Código | Estado |
|---|---|---|---|---|
| 00 | Mapa general | ¿Qué piezas tiene un sistema web y por dónde viaja una venta? | No tiene | Disponible |
| 01 | HTTP y REST | ¿Cómo se entienden dos programas que no comparten lenguaje? | [`etapas/01_http`](etapas/01_http/README.md) | Disponible |
| 02 | FastAPI desde cero | ¿Cómo se arranca un servidor y se define una ruta? | `etapas/02_fastapi_basico` | Pendiente |
| 03 | FastAPI estructurado | ¿Cómo se divide el backend y qué aporta cada división? | `etapas/03_fastapi_estructurado` | Pendiente |
| 04 | Diseño de la base de datos | ¿Cómo se pasa de una planilla a tablas normalizadas? | `etapas/04_base_de_datos` | Pendiente |
| 05 | Backend ↔ base de datos | ¿Cómo lee y escribe el backend en MariaDB sin perder datos? | `etapas/05_backend_base` | Pendiente |
| 06 | Seguridad | ¿Cómo se guardan las contraseñas y se identifica a quien hace cada petición? | `etapas/06_seguridad` | Pendiente |
| 07 | JavaScript vs TypeScript | ¿Qué agrega TypeScript y cuánto cuesta usarlo? | `etapas/07_js_vs_ts` | Pendiente |
| 08 | React + Vite | ¿Cómo se crea, declara e inicializa una interfaz hecha con componentes? | `etapas/08_react_vite` | Pendiente |
| 09 | Frontend ↔ backend | ¿Cómo consume React la API y cómo maneja el inicio de sesión? | `etapas/09_front_back` | Pendiente |
| 10 | Docker Compose | ¿Cómo se empaqueta todo lo que antes se ejecutó a mano? | `etapas/10_docker_compose` | Pendiente |

## Estructura de carpetas

```
aprendizaje/
├── README.md                     ← este archivo
├── explicaciones_didacticas/
│   ├── index.html                ← punto de entrada
│   ├── comun/                    ← estilos y motor de animaciones compartidos
│   ├── 00_mapa_general.html
│   └── 01_http_rest.html
└── etapas/                       ← código ejecutable, una carpeta por módulo
    └── 01_http/
```

## Requisitos

| Herramienta | Versión instalada | Desde qué módulo se usa |
|---|---|---|
| Python | 3.12 | 01 |
| Node.js | 24 | 07 |
| Docker Desktop | 29 | 04 (solo para el contenedor de MariaDB) |
| git | 2.52 | Siempre |

## Decisiones acordadas

| Decisión | Motivo |
|---|---|
| Un único caso de uso: un mini Punto Lácteo | Cada concepto se explica con un problema del negocio real. |
| Etapas de código progresivas y ejecutables por separado | Comparar dos etapas muestra exactamente qué agrega cada concepto. |
| Un HTML por módulo, con estilos y motor de animación compartidos en `comun/` | Todos los módulos tienen el mismo formato y funcionan sin internet. |
| MariaDB en un contenedor; backend y frontend ejecutados directamente en la PC | Los registros y los errores se ven sin capas intermedias. Docker completo recién en el módulo 10. |
| La base de datos primero en SQL escrito a mano, después con SQLAlchemy y Alembic | Permite entender qué hace el ORM por debajo. |
| React + TypeScript + Vite con CSS simple | Se aprenden los fundamentos sin librerías. Mantine se explica en el módulo 08 y se usa en el proyecto real. |
| Token *Bearer* guardado en `localStorage` | Es lo que muestra la documentación oficial de FastAPI. El módulo 06 explica el riesgo y la alternativa con cookie `httpOnly`. |
| Dominio en español (`producto`, `venta`), términos de los frameworks en inglés (`router`, `schema`) y comentarios en español | El código habla el idioma del negocio sin traducir los nombres de las herramientas. |
| `venv` + `pip` + `requirements.txt` | Es lo que usa la documentación oficial de Python y de FastAPI. |
| El bot de Telegram queda fuera de este material | Se aprende más adelante, junto con sus requisitos específicos. |
| Un commit por módulo terminado | `git log` muestra la historia y `git diff` permite comparar etapas. |
