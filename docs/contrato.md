# Contrato del MVP de Punto Lácteo

Este documento es la **única fuente de verdad** compartida por el backend, el frontend y el bot. Si una parte necesita algo que no está acá, se agrega acá primero.

## Convenciones

- **Idioma:** nombres del dominio en español, términos de los frameworks en inglés y comentarios en español (voseo en los textos para el usuario: «Ingresá», «No tenés permiso»).
- **Dinero:** `DECIMAL(12,2)`. **Cantidades** (kg con gramos o unidades): `DECIMAL(10,3)`. En Python se usa `Decimal` y en JSON viajan como **texto** (`"0.350"`, `"7275.00"`). Los totales se redondean con `quantize(Decimal("0.01"), ROUND_HALF_UP)`.
- **Fechas:** `DATETIME` local de Argentina (todos los contenedores tienen `TZ=America/Argentina/Buenos_Aires`). En JSON van en ISO 8601 sin zona (`"2026-11-15T10:32:00"`).
- **Roles:** `duenio` y `empleado`. El empleado pertenece a una sucursal y solo opera en ella. La dueña tiene `sucursal_id = NULL` y opera en cualquiera, pasando `sucursal_id`.
- **Errores:** `{"detail": "texto en español"}`. Los códigos son 401 (sin sesión o sesión vencida), 403 (rol o sucursal sin permiso), 404 (no existe), 409 (regla del negocio: sin stock, caja cerrada, nombre repetido…) y 422 (datos inválidos).

## Base de datos (MariaDB 11.4, utf8mb4, base `punto_lacteo`)

El esquema lo crea Alembic desde el backend. El resto de los componentes solo lo lee.

| Tabla | Columnas (todas `NOT NULL` salvo que diga `NULL`) |
|---|---|
| `sucursal` | `id` PK · `nombre` VARCHAR(60) UNIQUE · `activa` BOOL default 1 |
| `usuario` | `id` PK · `nombre_usuario` VARCHAR(40) UNIQUE (login) · `nombre` VARCHAR(80) · `password_hash` VARCHAR(255) · `rol` VARCHAR(10) CHECK IN ('duenio','empleado') · `sucursal_id` FK NULL · `activo` BOOL default 1 · `telegram_id` BIGINT NULL UNIQUE · `creado_en` DATETIME default now · CHECK (`rol`='duenio' OR `sucursal_id` IS NOT NULL) |
| `producto` | `id` PK · `nombre` VARCHAR(80) UNIQUE · `unidad` VARCHAR(10) CHECK IN ('kg','unidad') · `modo_precio` VARCHAR(10) CHECK IN ('manual','margen') default 'manual' · `margen` DECIMAL(6,2) NULL (porcentaje: 35 = 35 %) · `costo_ultimo` DECIMAL(12,2) NULL · `precio` DECIMAL(12,2) CHECK > 0 · `activo` BOOL default 1 · `creado_en` DATETIME default now · CHECK (`modo_precio`='manual' OR `margen` IS NOT NULL) |
| `stock` | PK (`producto_id`, `sucursal_id`), ambas FK · `cantidad` DECIMAL(10,3) default 0 CHECK >= 0 (saldo) · `minimo` DECIMAL(10,3) default 0 CHECK >= 0 |
| `movimiento_stock` | `id` PK · `producto_id` FK · `sucursal_id` FK · `tipo` VARCHAR(20) · `cantidad` DECIMAL(10,3) con signo · `saldo_resultante` DECIMAL(10,3) · `usuario_id` FK · `motivo` VARCHAR(200) NULL · `venta_id` FK NULL · `compra_id` FK NULL · `traspaso_id` FK NULL · `fecha` DATETIME default now · índice (`producto_id`, `sucursal_id`, `fecha`) |
| `traspaso` | `id` PK · `producto_id` FK · `origen_id` FK sucursal · `destino_id` FK sucursal · `cantidad` DECIMAL(10,3) CHECK > 0 · `usuario_id` FK · `motivo` VARCHAR(200) NULL · `fecha` DATETIME default now · CHECK (`origen_id` <> `destino_id`) |
| `caja` | `id` PK · `sucursal_id` FK · `estado` VARCHAR(10) CHECK IN ('abierta','cerrada') · `abierta_por` FK usuario · `abierta_en` DATETIME default now · `fondo_inicial` DECIMAL(12,2) CHECK >= 0 · `cerrada_por` FK NULL · `cerrada_en` NULL · `efectivo_esperado` DECIMAL(12,2) NULL · `efectivo_contado` DECIMAL(12,2) NULL · `diferencia` DECIMAL(12,2) NULL (contado − esperado) · `observacion` VARCHAR(200) NULL |
| `venta` | `id` PK · `sucursal_id` FK · `caja_id` FK · `usuario_id` FK · `fecha` DATETIME default now · `medio_pago` VARCHAR(15) CHECK IN ('efectivo','transferencia') · `total` DECIMAL(12,2) · `estado` VARCHAR(10) CHECK IN ('valida','observada','anulada') default 'valida' · `motivo_observacion` VARCHAR(200) NULL · `observada_por` FK NULL · `observada_en` NULL · `motivo_resolucion` VARCHAR(200) NULL · `resuelta_por` FK NULL · `resuelta_en` NULL · índice (`sucursal_id`, `fecha`) |
| `venta_detalle` | PK (`venta_id`, `producto_id`) · `cantidad` DECIMAL(10,3) CHECK > 0 · `precio_unitario` DECIMAL(12,2) (copia histórica) · `subtotal` DECIMAL(12,2) |
| `proveedor` | `id` PK · `nombre` VARCHAR(80) UNIQUE · `telefono` VARCHAR(40) NULL · `email` VARCHAR(120) NULL · `notas` VARCHAR(200) NULL · `activo` BOOL default 1 |
| `compra` | `id` PK · `proveedor_id` FK · `sucursal_id` FK · `usuario_id` FK · `fecha` DATETIME default now · `comprobante` VARCHAR(40) NULL · `total` DECIMAL(12,2) |
| `compra_detalle` | PK (`compra_id`, `producto_id`) · `cantidad` DECIMAL(10,3) CHECK > 0 · `costo_unitario` DECIMAL(12,2) CHECK >= 0 · `subtotal` DECIMAL(12,2) |
| `notificacion` | `id` PK · `tipo` VARCHAR(30) CHECK IN ('stock_bajo','venta_observada','merma','ajuste','diferencia_caja') · `sucursal_id` FK NULL · `mensaje` VARCHAR(500) (texto listo para enviar por Telegram) · `creada_en` DATETIME default now |

**Tipos de movimiento y signo.** Lo controla un CHECK en `movimiento_stock`:
- `compra` > 0
- `venta` < 0
- `merma` < 0
- `ajuste` ≠ 0
- `traspaso_salida` < 0
- `traspaso_entrada` > 0
- `anulacion` > 0

Otro CHECK exige `motivo` para `merma`, `ajuste` y `anulacion`.

**Usuarios de la base:**
- `MARIADB_USER`, para el backend: todos los permisos sobre `punto_lacteo` y `punto_lacteo_test`.
- `TB_DB_USER`, para el bot: solo `SELECT` sobre `punto_lacteo`.

Los dos los crea la imagen de MariaDB y `mariadb/init/01_inicial.sh`.

## Reglas del negocio

1. **Cada cambio de stock** actualiza `stock.cantidad` e inserta un `movimiento_stock` con el `saldo_resultante`, todo en **la misma transacción**. Las filas de `stock` se bloquean con `SELECT … FOR UPDATE`, ordenadas por `producto_id`, para evitar deadlocks. El stock nunca queda negativo: si no alcanza, responde 409.
2. **Alerta de stock bajo.** Si un movimiento hace que el saldo **cruce** el mínimo (antes `>= minimo`, después `< minimo`, con `minimo > 0`), se inserta una `notificacion` de tipo `stock_bajo` en la misma transacción. Si el saldo ya estaba por debajo, no se repite.
3. **Venta.** Requiere una caja `abierta` en la sucursal (si no, 409 «La caja de la sucursal está cerrada»). Las líneas del mismo producto se suman, los productos tienen que estar activos, y los vendidos por `unidad` exigen una cantidad entera (422). El `precio_unitario` es `producto.precio` y el `subtotal` es `cantidad × precio` redondeado. Se genera un movimiento `venta` por línea.
4. **Observar una venta.** Lo puede hacer cualquier rol: el empleado solo en su sucursal, y la dueña en cualquiera. Pasa de `valida` a `observada` con motivo obligatorio y genera una `notificacion` `venta_observada`. **No** devuelve stock.
5. **Confirmar o anular** (solo la dueña):
   - **Confirmar:** `observada` → `valida`.
   - **Anular:** `valida` u `observada` → `anulada`, con motivo obligatorio. Devuelve el stock con movimientos `anulacion`.
   - Para ambas, la venta tiene que estar en el estado correcto (si no, 409).
6. **Totales y reportes:** solo cuentan las ventas `valida`.
7. **Caja.** Hay una sola caja abierta por sucursal (409 si ya hay una).
   - **Esperado** = `fondo_inicial` + suma del `total` de las ventas en `efectivo` de esa caja **no anuladas**.
   - **Diferencia** = contado − esperado. Si es distinta de 0, se genera una `notificacion` `diferencia_caja`.
8. **Merma o ajuste.** Lo hace cualquier rol en su sucursal, con motivo obligatorio. La merma se informa como una cantidad positiva y se guarda negativa; el ajuste lleva signo. Genera una `notificacion` `merma` o `ajuste` y aplica la regla 2.
9. **Traspaso** (solo la dueña). Un registro en `traspaso` más dos movimientos (`traspaso_salida` en el origen y `traspaso_entrada` en el destino) en una transacción. Aplica la regla 2 en el origen.
10. **Compra** (solo la dueña). Genera movimientos `compra` y actualiza `producto.costo_ultimo`. Si el producto está en `modo_precio = 'margen'`, recalcula `precio = costo × (1 + margen/100)` redondeado.
11. **Producto nuevo** (solo la dueña). Se crean filas de `stock` en cero para **todas** las sucursales, con el mínimo indicado para cada una (0 por defecto). Si el modo es `margen` y hay `costo_ultimo`, el precio se calcula; si no, `precio` es obligatorio.
12. **El empleado no ve costos ni márgenes.** Las respuestas de productos para el empleado omiten `costo_ultimo`, `margen` y `modo_precio`.
13. **Mensajes de `notificacion`.** Texto corto en español, listo para Telegram. Ejemplos:
    - «⚠️ Stock bajo en Sucursal 1: Queso cremoso quedó en 1,750 kg (mínimo 2,000 kg).»
    - «👀 Venta 15 observada en Sucursal 2 por Bruno: cobró de más.»
    - «🗑️ Merma en Sucursal 1: Yogur bebible 1 L −2 u. (Carla): vencido.»
    - «💵 Caja de Sucursal 1 cerrada con diferencia de −$1.200,00 (esperado $45.300,00, contado $44.100,00).»

    En los mensajes, los números van con coma decimal.

## API (FastAPI)

El backend expone las rutas **sin** prefijo. nginx (producción) y Vite (desarrollo) reenvían `/api/*` a `http://backend:8000/*` quitando el `/api`. Hay autenticación Bearer JWT en todo, salvo `POST /auth/token`.

En la tabla, **D** es solo la dueña y **E/D** es cualquier rol. «Sucursal» indica que el empleado solo puede usar la suya: si manda otra, recibe 403. Si el empleado no manda `sucursal_id`, se usa la suya.

| Método y ruta | Rol | Cuerpo / parámetros → respuesta |
|---|---|---|
| `POST /auth/token` | — | Formulario OAuth2 (`username`=nombre_usuario, `password`) → `{access_token, token_type:"bearer"}`. Un usuario inactivo recibe 401 |
| `GET /auth/yo` | E/D | → `Usuario` |
| `GET /sucursales` | E/D | → `[{id, nombre, activa}]` |
| `PATCH /sucursales/{id}` | D | `{nombre}` → sucursal |
| `GET /usuarios` | D | → `[Usuario]` |
| `POST /usuarios` | D | `{nombre_usuario, nombre, contrasena (min 6), rol, sucursal_id?}` → `Usuario` (201) |
| `PATCH /usuarios/{id}` | D | `{nombre?, rol?, sucursal_id?, activo?, telegram_id?}` → `Usuario`. La dueña no puede desactivarse a sí misma (409) |
| `PUT /usuarios/{id}/contrasena` | D | `{contrasena}` → 204 |
| `GET /productos` | E/D | `?incluir_inactivos=false&buscar=` → `[Producto]` (versión según el rol, regla 12) |
| `POST /productos` | D | `{nombre, unidad, modo_precio, margen?, costo_ultimo?, precio?, minimos?: {"<sucursal_id>": "2.000"}}` → `Producto` (201) |
| `PATCH /productos/{id}` | D | Los mismos campos, opcionales, más `activo` → `Producto` |
| `PUT /productos/{id}/minimos` | D | `{"<sucursal_id>": "2.000", …}` → 204 |
| `GET /stock` | E/D | `?sucursal_id` (sucursal) → `[{producto_id, nombre, unidad, precio, cantidad, minimo, bajo_minimo}]`, solo los productos activos |
| `GET /stock/movimientos` | E/D | `?sucursal_id&producto_id?&tipo?&desde?&hasta?&limite=100` (sucursal) → `[{id, fecha, producto_id, producto, unidad, sucursal_id, tipo, cantidad, saldo_resultante, usuario, motivo, venta_id, compra_id, traspaso_id}]`, del más nuevo al más viejo |
| `POST /stock/movimientos` | E/D | `{sucursal_id?, producto_id, tipo:"merma"\|"ajuste", cantidad, motivo}` (sucursal) → movimiento (201) |
| `POST /stock/traspasos` | D | `{producto_id, origen_id, destino_id, cantidad, motivo?}` → `{id, …}` (201) |
| `GET /cajas/actual` | E/D | `?sucursal_id` (sucursal) → `CajaActual` o `null` |
| `POST /cajas` | E/D | `{sucursal_id?, fondo_inicial}` (sucursal) → `Caja` (201) |
| `POST /cajas/{id}/cerrar` | E/D | `{efectivo_contado, observacion?}` (sucursal de la caja) → `Caja` |
| `GET /cajas` | D | `?sucursal_id?&desde?&hasta?` → `[Caja]` |
| `POST /ventas` | E/D | `{sucursal_id?, medio_pago, items:[{producto_id, cantidad}]}` (sucursal) → `Venta` (201) |
| `GET /ventas` | E/D | `?sucursal_id&desde?&hasta?&estado?&limite=200` (sucursal; el empleado solo ve las de **hoy** de su sucursal) → `[Venta]`, de la más nueva a la más vieja |
| `GET /ventas/{id}` | E/D | (sucursal) → `Venta` |
| `POST /ventas/{id}/observar` | E/D | `{motivo}` (sucursal) → `Venta` |
| `POST /ventas/{id}/confirmar` | D | `{motivo?}` → `Venta` |
| `POST /ventas/{id}/anular` | D | `{motivo}` → `Venta` |
| `GET /proveedores` | D | `?incluir_inactivos=false` → `[Proveedor]` |
| `POST /proveedores` | D | `{nombre, telefono?, email?, notas?}` → `Proveedor` (201) |
| `PATCH /proveedores/{id}` | D | Los mismos campos, opcionales, más `activo` → `Proveedor` |
| `GET /compras` | D | `?sucursal_id?&proveedor_id?&desde?&hasta?` → `[Compra]` |
| `POST /compras` | D | `{proveedor_id, sucursal_id, comprobante?, items:[{producto_id, cantidad, costo_unitario}]}` → `Compra` (201) |
| `GET /reportes/resumen` | D | `?desde&hasta&sucursal_id?` → `Resumen` |
| `GET /reportes/ventas-diarias` | D | `?desde&hasta&sucursal_id?` → `[{fecha:"2026-11-15", sucursal_id, total, cantidad}]` |

`desde` y `hasta` son fechas `YYYY-MM-DD`, ambas **inclusivas**.

### Esquemas de respuesta

```jsonc
// Usuario
{"id":1,"nombre_usuario":"ana","nombre":"Ana","rol":"duenio","sucursal_id":null,"activo":true,"telegram_id":null}

// Producto (dueña); el empleado recibe el mismo objeto sin modo_precio, margen ni costo_ultimo
{"id":1,"nombre":"Queso cremoso","unidad":"kg","precio":"12500.00","activo":true,
 "modo_precio":"margen","margen":"35.00","costo_ultimo":"9259.26",
 "stock":[{"sucursal_id":1,"cantidad":"4.200","minimo":"2.000"},{"sucursal_id":2,"cantidad":"1.500","minimo":"1.000"}]}

// Venta
{"id":15,"fecha":"2026-11-15T10:32:00","sucursal_id":1,"caja_id":3,"usuario_id":2,"usuario":"Bruno",
 "medio_pago":"efectivo","total":"7275.00","estado":"valida",
 "motivo_observacion":null,"observada_por":null,"observada_en":null,
 "motivo_resolucion":null,"resuelta_por":null,"resuelta_en":null,
 "items":[{"producto_id":1,"producto":"Queso cremoso","unidad":"kg","cantidad":"0.350","precio_unitario":"12500.00","subtotal":"4375.00"}]}

// Caja
{"id":3,"sucursal_id":1,"estado":"abierta","abierta_por":"Bruno","abierta_en":"…","fondo_inicial":"10000.00",
 "cerrada_por":null,"cerrada_en":null,"efectivo_esperado":null,"efectivo_contado":null,"diferencia":null,"observacion":null}

// CajaActual = Caja + resumen en vivo de sus ventas no anuladas
{ /* …Caja… */ "ventas_efectivo":"35300.00","ventas_transferencia":"12000.00","cantidad_ventas":9,"efectivo_esperado_actual":"45300.00"}

// Proveedor
{"id":1,"nombre":"Lácteos del Sur","telefono":null,"email":null,"notas":null,"activo":true}

// Compra
{"id":4,"fecha":"…","proveedor_id":1,"proveedor":"Lácteos del Sur","sucursal_id":1,"usuario":"Ana","comprobante":"R-0012","total":"98000.00",
 "items":[{"producto_id":1,"producto":"Queso cremoso","unidad":"kg","cantidad":"10.000","costo_unitario":"9800.00","subtotal":"98000.00"}]}

// Resumen (solo ventas 'valida' para los totales)
{"desde":"2026-11-09","hasta":"2026-11-15","total":"523400.00","cantidad_ventas":87,
 "por_medio":{"efectivo":"310000.00","transferencia":"213400.00"},
 "por_sucursal":[{"sucursal_id":1,"nombre":"Sucursal 1","total":"300000.00","cantidad_ventas":50}],
 "top_productos":[{"producto_id":1,"nombre":"Queso cremoso","unidad":"kg","cantidad":"12.350","total":"154375.00"}],
 "ventas_observadas":2,"ventas_anuladas":1,
 "mermas_y_ajustes":[{"fecha":"…","sucursal_id":1,"producto":"Yogur bebible 1 L","unidad":"unidad","tipo":"merma","cantidad":"-2.000","usuario":"Carla","motivo":"vencido"}],
 "diferencias_caja":[{"caja_id":3,"sucursal_id":1,"cerrada_en":"…","diferencia":"-1200.00"}]}
```

## Datos iniciales (semilla, solo si la base está vacía)

- **Sucursales:** «Sucursal 1» y «Sucursal 2».
- **Dueña:** `DUENIA_USUARIO`, `DUENIA_NOMBRE` y `DUENIA_CONTRASENA`, tomados de `.env`.
- **Empleados:** `bruno` en la Sucursal 1 y `carla` en la Sucursal 2, los dos con la contraseña `SEMILLA_CONTRASENA_EMPLEADOS` de `.env`.
- **Productos:** unos 12 productos reales del rubro, con stock inicial cargado como movimientos `ajuste` con motivo «Stock inicial». Por ejemplo, quesos y fiambres por kg y leche, yogur o manteca por unidad, algunos con modo `margen`.
- **Proveedores:** 2.

## Infraestructura

| Servicio | `container_name` | Puertos en la PC |
|---|---|---|
| `mariadb` (mariadb:11.4) | `puntolacteo-mariadb` | `127.0.0.1:3310` → 3306 (para desarrollo y pruebas) |
| `backend` (python:3.12-slim) | `puntolacteo-backend` | `127.0.0.1:8001` → 8000 (`/docs`) |
| `frontend` (node:24-alpine → nginx:1.29-alpine) | `puntolacteo-frontend` | `8090` → 80 |
| `telegrambot` (python:3.11-slim) | `puntolacteo-telegrambot` | — |
| `phpmyadmin` (phpmyadmin:5.2) | `puntolacteo-phpmyadmin` | `8091` → 80 |

Variables en `.env` (`.env.sample` en el repositorio): `MARIADB_ROOT_PASSWORD`, `MARIADB_DB`, `MARIADB_USER`, `MARIADB_USER_PASS`, `MARIADB_SERVER`, `TB_DB_USER`, `TB_DB_PASS`, `TB_TOKEN`, `CLAVE_SECRETA`, `DUENIA_USUARIO`, `DUENIA_NOMBRE`, `DUENIA_CONTRASENA` y `SEMILLA_CONTRASENA_EMPLEADOS`.

- **Desarrollo del backend fuera de Docker:** `DATABASE_URL=mariadb+pymysql://<MARIADB_USER>:<MARIADB_USER_PASS>@127.0.0.1:3310/punto_lacteo?charset=utf8mb4`.
- **Pruebas:** usan `punto_lacteo_test`.
