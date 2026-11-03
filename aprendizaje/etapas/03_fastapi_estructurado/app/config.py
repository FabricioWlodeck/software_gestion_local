"""
Configuración de la aplicación en un solo lugar.

Los valores que cambian entre la PC de desarrollo y el servidor se leen de
variables de entorno, con un valor por defecto para desarrollar sin configurar nada.
"""

import os

NOMBRE_APP = "Punto Lácteo · etapa 03"
VERSION = "0.3.0"

# Mismo texto fijo que en las etapas 01 y 02. El módulo 06 lo reemplaza por JWT.
TOKEN_DE_PRUEBA = os.getenv("TOKEN_DE_PRUEBA", "token-de-prueba-123")
