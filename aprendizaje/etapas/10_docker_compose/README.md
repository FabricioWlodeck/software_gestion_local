# Etapa 10: Docker Compose

Esta etapa acompaña al módulo [10, Docker Compose](../../explicaciones_didacticas/10_docker_compose.html). Empaqueta todo lo que en los módulos anteriores se ejecutaba a mano: la base (etapa 04), el backend (etapa 06) y el frontend (etapa 09). No tiene código propio: usa el de esas etapas.

| Archivo | Qué hace |
|---|---|
| `compose.yaml` | Declara los tres servicios (`db`, `api`, `web`), el volumen de datos y cómo se conectan |
| `api.Dockerfile` | Receta de la imagen del backend, con `06_seguridad` como contexto |
| `web.Dockerfile` | Receta en dos etapas: construye el frontend con Node y lo sirve con nginx |
| `*.dockerignore` | Lo que no se copia a cada imagen (por ejemplo, `node_modules`) |
| `nginx.conf` | Sirve el frontend y reenvía `/api` al backend, como el proxy de Vite |
| `.env.ejemplo` | Plantilla de las contraseñas y la clave secreta |

## Preparación (una vez)

1. Docker Desktop abierto.
2. Copiar `.env.ejemplo` como `.env` en esta carpeta y completar los valores. La clave secreta se genera con:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

`.env` no se sube a git. Si ya existe un `.env` en esta carpeta (se generó uno con valores aleatorios al probar la etapa), se puede usar tal cual.

## Cómo se ejecuta

Desde esta carpeta:

```bash
docker compose up -d --build
```

La primera vez descarga las imágenes base y construye las propias, así que tarda unos minutos. Después se abre <http://localhost:8081> y se inicia sesión con los usuarios de prueba de la etapa 06.

Se usa el puerto 8081 porque el 8080 lo ocupa el phpMyAdmin de la materia IoT. La base no publica ningún puerto: solo la ven los servicios de la red de Compose.

## Comandos útiles

| Comando | Qué hace |
|---|---|
| `docker compose ps` | Estado de cada servicio |
| `docker compose logs -f api` | Registros del backend en vivo (`Ctrl+C` para salir) |
| `docker compose exec db mariadb -u pl -p punto_lacteo` | Consola SQL dentro del contenedor de la base |
| `docker compose up -d --build` | Reconstruye lo que cambió y reinicia lo necesario |
| `docker compose down` | Detiene y borra los contenedores y la red. **Los datos quedan** en el volumen |
| `docker compose down -v` | Además borra el volumen: **se pierden todas las ventas** |

## Qué observar

1. En `docker compose logs api`, el primer arranque aplica las migraciones `0001` y `0002` y carga los datos iniciales. Los arranques siguientes no repiten nada.
2. `DATABASE_URL` usa `db:3306`, no `127.0.0.1:3307`: dentro de la red de Compose, cada servicio se llama por su nombre.
3. Después de `docker compose down` y `up -d`, las ventas siguen ahí, porque viven en el volumen `punto-lacteo_datos`.
4. La imagen del frontend pesa unos 93 MB y no contiene Node: solo nginx y los archivos de `dist/`.
