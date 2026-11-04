# Aprendizaje: cómo se conecta un sistema web con FastAPI, MariaDB y React

Este material sirve para entender cada pieza del sistema de Punto Lácteo antes de diseñarlo. En lugar de leer documentación suelta, se construye un mini Punto Lácteo reducido a tres entidades (productos, ventas y usuarios). Cada módulo agrega una sola pieza sobre el anterior.

El mini proyecto no es la base del sistema real. El MVP (*Minimum Viable Product* o Producto Mínimo Viable) se escribe desde cero aplicando lo aprendido. Este material se conserva como referencia.

## Cómo se estudia cada módulo

1. Abrir [`explicaciones_didacticas/index.html`](explicaciones_didacticas/index.html) con doble clic. Se abre en el navegador y no necesita internet.
2. Leer el módulo en orden. Todos tienen las mismas ocho secciones: problema, concepto, código mínimo, cómo se conecta, animación, errores comunes, ejercicios y documentación oficial.
3. Recorrer la animación con los botones o con las flechas del teclado.
4. Ejecutar la etapa de código correspondiente siguiendo su `README.md`.
5. Resolver los ejercicios antes de abrir las respuestas.

Cada módulo está pensado para estudiarse en 45 a 100 minutos; el índice indica la duración de cada uno.

## Temario

| # | Módulo | Pregunta que responde | Código | Estado |
|---|---|---|---|---|
| 00 | Mapa general | ¿Qué piezas tiene un sistema web y por dónde viaja una venta? | No tiene | Disponible |
| 01 | HTTP y REST | ¿Cómo se entienden dos programas que no comparten lenguaje? | [`etapas/01_http`](etapas/01_http/README.md) | Disponible |
| 02 | FastAPI desde cero | ¿Cómo se arranca un servidor y se define una ruta? | [`etapas/02_fastapi_basico`](etapas/02_fastapi_basico/README.md) | Disponible |
| 03 | FastAPI estructurado | ¿Cómo se divide el backend y qué aporta cada división? | [`etapas/03_fastapi_estructurado`](etapas/03_fastapi_estructurado/README.md) | Disponible |
| 04 | Diseño de la base de datos | ¿Cómo se pasa de una planilla a tablas normalizadas? | [`etapas/04_base_de_datos`](etapas/04_base_de_datos/README.md) | Disponible |
| 05 | Backend ↔ base de datos | ¿Cómo lee y escribe el backend en MariaDB sin perder datos? | [`etapas/05_backend_base`](etapas/05_backend_base/README.md) | Disponible |
| 06 | Seguridad | ¿Cómo se guardan las contraseñas y se identifica a quien hace cada petición? | [`etapas/06_seguridad`](etapas/06_seguridad/README.md) | Disponible |
| 07 | JavaScript vs TypeScript | ¿Qué agrega TypeScript y cuánto cuesta usarlo? | [`etapas/07_js_vs_ts`](etapas/07_js_vs_ts/README.md) | Disponible |
| 08 | React + Vite | ¿Cómo se crea, declara e inicializa una interfaz hecha con componentes? | [`etapas/08_react_vite`](etapas/08_react_vite/README.md) | Disponible |
| 09 | Frontend ↔ backend | ¿Cómo consume React la API y cómo maneja el inicio de sesión? | [`etapas/09_front_back`](etapas/09_front_back/README.md) | Disponible |
| 10 | Docker Compose | ¿Cómo se empaqueta todo lo que antes se ejecutó a mano? | [`etapas/10_docker_compose`](etapas/10_docker_compose/README.md) | Disponible |
| 11 | Patrones de diseño | ¿Qué patrones ya aparecieron, cuáles hacen falta en el sistema real y cómo se decide cuándo usar uno? | [`etapas/11_patrones`](etapas/11_patrones/README.md) | Disponible |

## Estructura de carpetas

```
aprendizaje/
├── README.md                       ← este archivo
├── .venv/                          ← entorno virtual compartido (git lo ignora; ver etapa 02)
├── explicaciones_didacticas/
│   ├── index.html                  ← punto de entrada
│   ├── comun/                      ← estilos y motor de animaciones compartidos
│   └── 00_mapa_general.html … 11_patrones_diseno.html
└── etapas/                         ← código ejecutable, una carpeta por módulo
    ├── 01_http/                    servidor y cliente HTTP con la biblioteca estándar
    ├── 02_fastapi_basico/          la misma API con FastAPI, en un archivo
    ├── 03_fastapi_estructurado/    capas: routers, schemas, services, repositories
    ├── 04_base_de_datos/           esquema, datos y consultas en SQL
    ├── 05_backend_base/            SQLAlchemy, transacciones y Alembic
    ├── 06_seguridad/               Argon2, JWT y roles
    ├── 07_js_vs_ts/                el mismo carrito en JavaScript y TypeScript
    ├── 08_react_vite/              la caja en React, con datos de prueba
    ├── 09_front_back/              la caja conectada a la API de la etapa 06
    ├── 10_docker_compose/          todo el sistema en contenedores
    └── 11_patrones/                libro de movimientos, estrategia, reducer y registros de decisiones
```

## Requisitos

| Herramienta | Versión instalada | Desde qué módulo se usa |
|---|---|---|
| Python | 3.12 | 01 |
| Node.js | 24 | 07 |
| Docker Desktop | 29 | 04 (MariaDB) y 10 (todo el sistema) |
| git | 2.52 | Siempre |

## Puertos

| Puerto en la PC | Qué lo usa | Módulos |
|---|---|---|
| 8000 | El backend, ejecutado con `fastapi dev` o con los servidores de la etapa 01 | 01 a 06, 09 |
| 3307 | El contenedor `pl-mariadb` (el 3306 lo usa el MariaDB de la materia IoT) | 04 a 06, 09 |
| 5173 | El servidor de desarrollo de Vite | 08 y 09 |
| 8081 | nginx de Docker Compose (el 8080 lo usa el phpMyAdmin de la materia IoT) | 10 |

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
