# Punto Lácteo: gestión de ventas y stock

Sistema de gestión de ventas, stock y caja para Punto Lácteo, un local de lácteos, fiambres y quesos con dos sucursales. Gran parte de lo que vende se vende por peso.

Tiene cuatro piezas que se levantan juntas con Docker Compose:

| Carpeta | Pieza | Tecnología |
|---|---|---|
| [`backend/`](backend/README.md) | API con las reglas del negocio | FastAPI, SQLAlchemy 2, Alembic, Argon2 y JWT |
| [`frontend/`](frontend/) | Interfaz para la caja y para la dueña | React 19, Vite, TypeScript y Mantine |
| [`telegrambot/`](telegrambot/) | Avisos y consultas para la dueña | python-telegram-bot, aiomysql y matplotlib |
| [`mariadb/`](mariadb/init/01_inicial.sh) | Base de datos | MariaDB 11.4 |

El contrato entre las piezas (tablas, rutas de la API y reglas) está en [`docs/contrato.md`](docs/contrato.md), y las decisiones de diseño, en [`docs/decisiones/`](docs/decisiones/). El material de estudio previo está en [`aprendizaje/`](aprendizaje/README.md).

## Qué hace

- **Venta:** búsqueda de productos, cantidad en kg o en unidades, cobro en efectivo o por transferencia. No se vende sin la caja abierta.
- **Caja:** se abre con un fondo inicial y se cierra contando el efectivo. Si el conteo no coincide, se registra la diferencia y se avisa a la dueña.
- **Stock por sucursal:** cada cambio queda en un libro de movimientos con quién, cuándo y por qué (ventas, compras, mermas, ajustes, traspasos y anulaciones).
- **Ventas observadas:** un empleado no puede anular una venta, pero la puede marcar como observada. La dueña la confirma o la anula, y si la anula, el stock vuelve.
- **Solo para la dueña:** productos y precios (manuales o con un margen sobre el último costo), compras y proveedores, traspasos entre sucursales, reportes, cierres de caja y empleados.
- **Bot de Telegram:** avisa a la dueña de stock bajo, ventas observadas, mermas, ajustes y diferencias de caja. Envía un resumen los lunes y el día 1 de cada mes, y responde consultas de stock y de ventas.

## Cómo se levanta

Hace falta Docker Desktop. Desde la raíz del repositorio:

1. Copiar `.env.sample` a `.env` y completar las contraseñas. `TB_TOKEN` puede quedar vacío: el bot espera sin hacer nada hasta que se cargue.
2. Levantar todo:

```bash
docker compose up -d --build
```

La primera vez, el backend crea las tablas y carga datos de prueba: dos sucursales, la dueña (con el usuario y la contraseña de `.env`), los empleados `bruno` y `carla`, 12 productos y 2 proveedores.

| Dirección | Qué hay |
|---|---|
| http://localhost:8090 | La aplicación |
| http://127.0.0.1:8001/docs | Documentación interactiva de la API |
| http://localhost:8091 | phpMyAdmin |

Para detener el sistema, `docker compose down`. Los datos quedan en el volumen `datos_mariadb`. **No** hay que usar `docker compose down -v`, porque borra la base de datos.

## Cómo se activa el bot

1. En Telegram, crear un bot nuevo con @BotFather (`/newbot`) y copiar el token a `TB_TOKEN` en `.env`. Tiene que ser un bot propio: si dos programas usan el mismo token, Telegram rechaza a uno de ellos.
2. Averiguar el telegram_id de la dueña con @userinfobot y cargarlo en la pantalla Empleados, en los datos de la dueña.
3. Aplicar el cambio:

```bash
docker compose up -d telegrambot
```

## Pruebas

```bash
docker compose run --rm --no-deps backend python -m pytest -q
```

Las pruebas usan una base aparte, `punto_lacteo_test`, que se recrea en cada corrida.

El bot tiene un modo de prueba que no necesita token: `docker compose exec telegrambot python /app/telegrambot.py --probar ventas-hoy`.

## Lo que viene

- Publicación con HTTPS mediante SWAG y DuckDNS, como en la materia IoT.
- Lotes con fecha de vencimiento y venta del lote que vence primero (FEFO, *First Expired, First Out* o Primero en Vencer, Primero en Salir).
- Pagos combinados, facturación, integración con la balanza y copias de seguridad automáticas.
