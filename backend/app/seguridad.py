"""
Hash de contraseñas y tokens JWT. No sabe nada de HTTP ni de la base de datos.

- Hash (Argon2): irreversible. Se puede comprobar si una contraseña coincide, pero no recuperarla.
- Firma (HMAC-SHA256 dentro del JWT): el token se puede leer, pero no modificar sin la clave secreta.
"""

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import ALGORITMO_JWT, CLAVE_SECRETA, MINUTOS_DE_SESION

hasheador = PasswordHash.recommended()  # Argon2 con parámetros recomendados

# Se verifica contra este hash cuando el usuario no existe, para que la respuesta tarde
# lo mismo y no revele qué nombres de usuario existen.
HASH_FICTICIO = hasheador.hash("contraseña-ficticia")


def hashear(contrasena: str) -> str:
    return hasheador.hash(contrasena)


def verificar(contrasena: str, hash_guardado: str) -> bool:
    return hasheador.verify(contrasena, hash_guardado)


def crear_token(usuario_id: int, rol: str) -> str:
    ahora = datetime.now(UTC)
    contenido = {
        "sub": str(usuario_id),  # a quién identifica el token
        "rol": rol,
        "iat": ahora,  # cuándo se emitió
        "exp": ahora + timedelta(minutes=MINUTOS_DE_SESION),  # cuándo vence
    }
    return jwt.encode(contenido, CLAVE_SECRETA, algorithm=ALGORITMO_JWT)


def leer_token(token: str) -> dict:
    """Devuelve el contenido si la firma es válida y no venció; si no, lanza jwt.InvalidTokenError."""
    return jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO_JWT], options={"require": ["sub", "exp"]})
