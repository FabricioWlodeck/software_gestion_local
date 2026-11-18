# Backend de Punto Lácteo

API REST con FastAPI, SQLAlchemy 2 y MariaDB. Implementa [`docs/contrato.md`](../docs/contrato.md): las tablas, las rutas, los roles y las reglas del negocio salen de ahí.

## Estructura

```
app/
  main.py          crea la app, incluye los routers y traduce los errores a {"detail": "…"}
  config.py        variables de entorno (lee el .env de la raíz si se trabaja fuera de Docker)
  database.py      engine, SesionLocal y la dependencia obtener_sesion
  models.py        las 13 tablas, con sus CHECK
  seguridad.py     Argon2 para las contraseñas y JWT para las sesiones (8 horas)
  dependencies.py  usuario actual (401), rol requerido (403) y un service por petición
  errores.py       errores del negocio, cada uno con su código HTTP
  formato.py       redondeos y números con coma decimal para los avisos
  semilla.py       datos iniciales (solo si no hay sucursales)
  routers/         HTTP → service (finos)
  schemas/         Pydantic: lo que entra y sale de la API
  services/        reglas del negocio y commit de cada transacción
    libro.py       el único lugar que cambia el stock (movimiento + saldo + aviso de mínimo)
    avisos.py      filas de notificacion que lee el bot de Telegram
  repositories/    consultas SQLAlchemy, con SELECT … FOR UPDATE donde hace falta
alembic/           migraciones (0001 crea el esquema)
tests/             pruebas de punta a punta contra punto_lacteo_test
```

## Desarrollo local (fuera de Docker)

Necesita el contenedor `puntolacteo-mariadb` levantado (publica `127.0.0.1:3310`). Desde `backend/`:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\alembic upgrade head        # crea las tablas en punto_lacteo
.venv\Scripts\python -m app.semilla       # carga los datos iniciales si la base está vacía
.venv\Scripts\fastapi dev app/main.py     # http://127.0.0.1:8000/docs
```

`app/config.py` lee el `.env` de la raíz del repositorio y arma
`mariadb+pymysql://<MARIADB_USER>:<MARIADB_USER_PASS>@127.0.0.1:3310/punto_lacteo?charset=utf8mb4`.
Si se define `DATABASE_URL`, se usa esa.

## Pruebas

```powershell
.venv\Scripts\python -m pytest
```

Usan la base `punto_lacteo_test` del mismo servidor (o `TEST_DATABASE_URL`). Al empezar recrean el esquema, y antes de cada prueba vacían las tablas y cargan dos sucursales, tres usuarios, dos productos y un proveedor. Las pruebas pasan por la API con `TestClient`, así que prueban routers, services y la base juntos.

## Cómo arranca la imagen

`docker compose up -d --build backend` construye `python:3.12-slim` con `TZ=America/Argentina/Buenos_Aires` y ejecuta:

1. `alembic upgrade head`: aplica las migraciones pendientes.
2. `python -m app.semilla`: carga los datos iniciales solo si no hay sucursales.
3. `fastapi run app/main.py --host 0.0.0.0 --port 8000`.

La documentación interactiva queda en http://127.0.0.1:8001/docs. Ahí, «Authorize» pide usuario y contraseña y obtiene el token.

## Decisiones que no están en el contrato

- Las fechas (`fecha`, `abierta_en`, `cerrada_en`, `observada_en`…) las pone MariaDB (`CURRENT_TIMESTAMP`), con un solo reloj para todo el sistema.
- Los errores de validación de Pydantic también responden `{"detail": "texto"}`, por ejemplo `"Datos inválidos: items.0.cantidad: tiene que ser mayor que 0"`.
- En `GET /ventas` y `GET /stock/movimientos` la dueña puede omitir `sucursal_id` para ver las dos sucursales. En `GET /stock`, `GET /cajas/actual`, `POST /cajas`, `POST /ventas` y `POST /stock/movimientos` lo tiene que mandar (422).
- Los productos por unidad exigen cantidades enteras en ventas, compras, mermas, ajustes y traspasos.
- Una compra no admite el mismo producto en dos líneas (422). Con costo 0, el precio en modo margen no se recalcula.
