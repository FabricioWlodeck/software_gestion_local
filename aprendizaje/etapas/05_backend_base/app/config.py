"""
Configuración de la aplicación en un solo lugar.

DATABASE_URL tiene la forma  dialecto+driver://usuario:contraseña@servidor:puerto/base
Cambiar de motor es cambiar este texto. Por ejemplo, para SQLite:
    $env:DATABASE_URL = "sqlite:///./punto_lacteo.db"
"""

import os

NOMBRE_APP = "Punto Lácteo · etapa 05"
VERSION = "0.5.0"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mariadb+pymysql://pl:pl123@127.0.0.1:3307/punto_lacteo_orm?charset=utf8mb4",
)

# True muestra en la terminal cada consulta SQL que genera SQLAlchemy.
MOSTRAR_SQL = os.getenv("MOSTRAR_SQL", "1") == "1"

TOKEN_DE_PRUEBA = os.getenv("TOKEN_DE_PRUEBA", "token-de-prueba-123")
