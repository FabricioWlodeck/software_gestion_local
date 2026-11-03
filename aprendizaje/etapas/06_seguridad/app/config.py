"""
Configuración de la aplicación en un solo lugar.

CLAVE_SECRETA firma los tokens: quien la conozca puede fabricar tokens válidos para
cualquier usuario. En el servidor se define con una variable de entorno y nunca se sube a git.
Para generar una:  python -c "import secrets; print(secrets.token_hex(32))"
"""

import os

NOMBRE_APP = "Punto Lácteo · etapa 06"
VERSION = "0.6.0"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mariadb+pymysql://pl:pl123@127.0.0.1:3307/punto_lacteo_orm?charset=utf8mb4",
)
MOSTRAR_SQL = os.getenv("MOSTRAR_SQL", "0") == "1"

# Valor de desarrollo, solo para aprender. En producción la variable de entorno es obligatoria.
CLAVE_SECRETA = os.getenv("CLAVE_SECRETA", "clave-de-desarrollo-cambiar-en-produccion")
ALGORITMO_JWT = "HS256"
MINUTOS_DE_SESION = int(os.getenv("MINUTOS_DE_SESION", "480"))  # un turno de 8 horas
