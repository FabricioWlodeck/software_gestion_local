# Etapa 11: patrones de diseño y registros de decisiones

Esta etapa acompaña al módulo [11, Patrones de diseño](../../explicaciones_didacticas/11_patrones_diseno.html). A diferencia de las anteriores, no es una versión nueva del mini Punto Lácteo: son tres ejemplos chicos, uno por capa, de patrones que el proyecto real va a necesitar, y cuatro registros de decisiones de arquitectura.

| Carpeta o archivo | Qué muestra |
|---|---|
| `bd/libro_de_movimientos.sql` | El stock como libro de movimientos, comparado con una columna que se sobrescribe |
| `backend/precios.py` | El patrón Estrategia para calcular el precio por margen o a mano, con una fábrica que elige la estrategia |
| `frontend/carritoReducer.ts` | La lógica del carrito como reducer: una función pura que se prueba sin React |
| `frontend/probar_carrito.ts` | La prueba del reducer, que se ejecuta con Node |
| `frontend/useCarrito.ts` | El hook personalizado que usa el reducer, para llevar a la etapa 08 o 09 (ejercicio 4) |
| `frontend/tipos.ts` | Copia de los tipos de la etapa 08, para que la carpeta funcione sola |
| `decisiones/` | La plantilla de un registro de decisión y tres ejemplos: dos decisiones ya tomadas en el material y una propuesta para el MVP |

## Cómo se ejecuta

Todos los comandos son para PowerShell y se ejecutan **desde la carpeta de esta etapa**.

### Base de datos: libro de movimientos

El contenedor `pl-mariadb` de la etapa 04 tiene que estar corriendo (`docker start pl-mariadb`). La primera vez se crea una base propia para esta etapa, para no mezclar tablas con las de los módulos 04 y 05:

```bash
docker exec pl-mariadb mariadb -u root -praiz123 -e "CREATE DATABASE IF NOT EXISTS punto_lacteo_patrones CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL PRIVILEGES ON punto_lacteo_patrones.* TO 'pl'@'%';"
```

El contenedor de la etapa 04 solo ve la carpeta `sql` de esa etapa, así que el script se copia adentro y después se ejecuta. `--force` hace que siga después de los dos errores que el script provoca a propósito al final:

```bash
docker cp bd/libro_de_movimientos.sql pl-mariadb:/tmp/libro_de_movimientos.sql
```

```bash
docker exec pl-mariadb mariadb -u pl -ppl123 --default-character-set=utf8mb4 --table --force punto_lacteo_patrones -e "source /tmp/libro_de_movimientos.sql"
```

### Backend: estrategia de precios

Con el entorno virtual de `aprendizaje/.venv` activado (ver la etapa 02). Solo usa la biblioteca estándar de Python:

```bash
python backend/precios.py
```

### Frontend: reducer del carrito

Node.js 24 ejecuta el archivo `.ts` sin instalar nada:

```bash
node frontend/probar_carrito.ts
```

`useCarrito.ts` importa React, así que no se ejecuta solo: se usa dentro de un proyecto de Vite. Para probarlo, copiá `carritoReducer.ts` y `useCarrito.ts` a `src/features/ventas/` de la etapa 08 y cambiá en los dos el import de `./tipos.ts` por `../../tipos`. El reducer no se llama `carrito.ts` porque Windows no distingue mayúsculas de minúsculas en los nombres de archivo, y `./Carrito` (el componente) y `./carrito` serían el mismo archivo para TypeScript.

## Patrones de los módulos anteriores

Casi todos los patrones del módulo ya están en el código de las etapas 03 a 10. La tabla sirve para encontrarlos.

| Patrón | Dónde está | Qué resuelve |
|---|---|---|
| Arquitectura en capas | `03_fastapi_estructurado/app/` (routers, services, repositories) | Cada capa cambia por un motivo distinto |
| Repository | `03_fastapi_estructurado/app/repositories/memoria.py` y `05_backend_base/app/repositories/` | El service no sabe si los datos están en memoria o en MariaDB |
| Service Layer | `06_seguridad/app/services/ventas.py` | Las reglas del negocio están en un solo lugar, usable desde la API o desde un script (`03_fastapi_estructurado/probar_service.py`) |
| Unit of Work | La `Session` de SQLAlchemy y el `commit()` de `06_seguridad/app/services/ventas.py` | Una venta se guarda entera o no se guarda |
| Inyección de dependencias | `06_seguridad/app/dependencies.py` (`Depends`) | El router recibe la sesión y el usuario sin crearlos |
| Fábrica | `requerir_rol()` en `06_seguridad/app/dependencies.py` | Una dependencia por rol sin repetir código |
| DTO (Data Transfer Object) | `06_seguridad/app/schemas/` frente a `app/models.py` | La API no expone columnas internas como `password_hash` |
| Errores de dominio traducidos a HTTP | `06_seguridad/app/errores.py` y el manejador de `app/main.py` | El service no sabe de códigos HTTP |
| Copia histórica | `venta_detalle.precio_unitario` en `04_base_de_datos/sql/01_esquema.sql` | Si cambia el precio, la venta vieja conserva el suyo |
| Desnormalización deliberada | `venta.total` en `04_base_de_datos/sql/01_esquema.sql` | El total no se recalcula en cada consulta |
| Bloqueo pesimista | `obtener_para_actualizar()` en `06_seguridad/app/repositories/productos.py` | Dos cajas no venden el mismo último kilo |
| Migraciones versionadas | `06_seguridad/alembic/versions/` | El esquema cambia igual en cada máquina |
| Estado local, elevado y derivado | `08_react_vite/src/features/ventas/` (`TarjetaProducto`, `PantallaVentas`, `Carrito`) | Cada dato vive en un solo componente y lo demás se calcula |
| Cliente de API centralizado | `09_front_back/src/api/cliente.ts` | Un solo archivo sabe de URLs, headers y tokens |
| Provider con hook propio | `09_front_back/src/features/auth/` (`SesionProvider.tsx`, `sesion.ts`) | Cualquier componente lee la sesión sin pasarla por props |
| Configuración por entorno | `06_seguridad/app/config.py` y `10_docker_compose/.env.ejemplo` | El mismo código sirve en la PC y en el servidor |
| Proxy inverso | `10_docker_compose/nginx.conf` | Una sola puerta de entrada para el frontend y la API |
