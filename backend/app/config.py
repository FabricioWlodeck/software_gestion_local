"""
Configuración de la aplicación en un solo lugar, leída de variables de entorno.

En Docker, compose.yaml define las variables. Fuera de Docker (desarrollo y pruebas),
si existe el .env de la raíz del repositorio se leen de ahí las que falten, y la base
se busca en 127.0.0.1:3310 (el puerto que publica el contenedor de MariaDB).
"""

import os
from pathlib import Path

from sqlalchemy.engine import make_url

NOMBRE_APP = "Punto Lácteo API"
VERSION = "1.0.0"

ARCHIVO_ENV_LOCAL = Path(__file__).resolve().parents[2] / ".env"


def _cargar_env_local() -> None:
    """Lee KEY=valor del .env de la raíz sin pisar las variables que ya existen."""
    if not ARCHIVO_ENV_LOCAL.is_file():
        return
    for linea in ARCHIVO_ENV_LOCAL.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


_cargar_env_local()


def _url_local() -> str:
    usuario = os.getenv("MARIADB_USER", "puntolacteo")
    contrasena = os.getenv("MARIADB_USER_PASS", "")
    base = os.getenv("MARIADB_DB", "punto_lacteo")
    return f"mariadb+pymysql://{usuario}:{contrasena}@127.0.0.1:3310/{base}?charset=utf8mb4"


DATABASE_URL = os.getenv("DATABASE_URL") or _url_local()
# Las pruebas usan la misma conexión con otra base, para no tocar los datos de desarrollo.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or make_url(DATABASE_URL).set(
    database="punto_lacteo_test"
).render_as_string(hide_password=False)
MOSTRAR_SQL = os.getenv("MOSTRAR_SQL", "0") == "1"

# CLAVE_SECRETA firma los tokens: quien la conozca puede fabricar tokens para cualquier usuario.
CLAVE_SECRETA = os.getenv("CLAVE_SECRETA") or "clave-de-desarrollo-cambiar-en-produccion"
ALGORITMO_JWT = "HS256"
MINUTOS_DE_SESION = int(os.getenv("MINUTOS_DE_SESION", "480"))  # un turno de 8 horas
