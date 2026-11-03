# Etapa 06: seguridad

Esta etapa acompaña al módulo [06, seguridad](../../explicaciones_didacticas/06_seguridad.html). Es la etapa 05 con usuarios que inician sesión: contraseñas guardadas con hash Argon2, tokens JWT firmados y permisos por rol. El token fijo de las etapas anteriores desaparece.

| Archivo nuevo o cambiado | Qué hace |
|---|---|
| `app/seguridad.py` | Hash y verificación de contraseñas; creación y lectura de tokens JWT |
| `app/routers/auth.py` | `POST /auth/token` (inicio de sesión) y `GET /auth/yo` (quién soy) |
| `app/dependencies.py` | Las guardias `obtener_usuario_actual` (401) y `requerir_rol` (403) |
| `app/routers/productos.py`, `ventas.py` | Cada ruta declara quién puede usarla |
| `app/schemas/venta.py` | `VentaIn` ya no trae `usuario_id`: sale del token |
| `alembic/versions/0002_...py` | Migración que agrega la columna `password_hash` |
| `app/semilla.py` | Asigna contraseñas de prueba a los usuarios |
| `explorar_seguridad.py` | Muestra por dentro un hash y un token, y qué pasa al alterarlo |

## Preparación

Usa la misma base que la etapa 05 (`punto_lacteo_orm`), que está en la migración `0001`. Con el entorno virtual activado, desde la carpeta `aprendizaje`:

```bash
pip install -r etapas/06_seguridad/requirements.txt
```

Desde la carpeta de esta etapa, se aplica solo la migración que falta y se asignan las contraseñas:

```bash
alembic upgrade head
```

```bash
python -m app.semilla
```

## Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| Ana | `ana123` | dueño |
| Bruno | `bruno123` | empleado |
| Carla | `carla123` | empleado |

Son contraseñas de prueba, a la vista a propósito. El nombre no distingue mayúsculas porque la base usa una intercalación (*collation*) que no las distingue.

## Cómo se ejecuta y se prueba

```bash
fastapi dev app/main.py
```

La forma más cómoda de probar es <http://127.0.0.1:8000/docs>: el botón **Authorize** pide usuario y contraseña, obtiene el token y lo agrega solo a cada petición.

Con `curl.exe` en PowerShell, primero se guarda el token en una variable:

```bash
$token = (curl.exe -s -X POST http://127.0.0.1:8000/auth/token -d "username=Bruno&password=bruno123" | ConvertFrom-Json).access_token
```

```bash
curl.exe -i http://127.0.0.1:8000/ventas -H "Authorization: Bearer $token"
```

Bruno recibe 403 al listar ventas: es empleado. Con el token de Ana, la misma petición responde 200.

Para ver el hash y el token por dentro, sin servidor:

```bash
python explorar_seguridad.py
```

## La clave secreta

`CLAVE_SECRETA` firma los tokens. La etapa trae un valor de desarrollo para aprender, pero en el servidor se define con una variable de entorno. Para generar una clave nueva:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Si la clave cambia, todos los tokens emitidos dejan de ser válidos y cada usuario tiene que volver a iniciar sesión.
