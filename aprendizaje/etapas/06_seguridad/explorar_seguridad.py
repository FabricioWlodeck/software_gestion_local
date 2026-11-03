"""
Muestra por dentro el hash de una contraseña y un token JWT, sin servidor ni base de datos.

Ejecutar desde la carpeta de la etapa:  python explorar_seguridad.py
"""

import base64
import json

import jwt

from app.seguridad import crear_token, hashear, leer_token, verificar


def decodificar_parte(parte: str) -> dict:
    """Decodifica una parte de un JWT. Es Base64URL: cualquiera puede hacerlo, no hace falta la clave."""
    relleno = "=" * (-len(parte) % 4)
    return json.loads(base64.urlsafe_b64decode(parte + relleno))


def codificar_parte(datos: dict) -> str:
    texto = json.dumps(datos, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(texto).rstrip(b"=").decode()


print("=== 1. HASH: la misma contraseña da hashes distintos ===")
hash_1 = hashear("bruno123")
hash_2 = hashear("bruno123")
print(f"hash 1: {hash_1}")
print(f"hash 2: {hash_2}")
print(f"¿son iguales?                        {hash_1 == hash_2}   (cada uno tiene su propia sal)")
print(f"verificar('bruno123', hash 1)        {verificar('bruno123', hash_1)}")
print(f"verificar('bruno123', hash 2)        {verificar('bruno123', hash_2)}")
print(f"verificar('bruno124', hash 1)        {verificar('bruno124', hash_1)}")

print("\n=== 2. JWT: tres partes separadas por puntos ===")
token = crear_token(usuario_id=2, rol="empleado")
encabezado, contenido, firma = token.split(".")
print(f"token completo:\n{token}\n")
print(f"encabezado (decodificado): {decodificar_parte(encabezado)}")
print(f"contenido  (decodificado): {decodificar_parte(contenido)}")
print(f"firma: {firma}   (no se decodifica: es el resultado de HMAC-SHA256 con la clave secreta)")

print("\n=== 3. Alguien cambia su rol a 'duenio' ===")
falso = decodificar_parte(contenido) | {"rol": "duenio"}
token_alterado = f"{encabezado}.{codificar_parte(falso)}.{firma}"
print(f"contenido alterado: {falso}")
try:
    leer_token(token_alterado)
    print("El servidor lo aceptó (esto no debería pasar)")
except jwt.InvalidSignatureError:
    print("El servidor lo rechaza: InvalidSignatureError. La firma no coincide con el contenido nuevo.")

print("\n=== 4. Un token firmado con otra clave ===")
otra_clave = "una-clave-distinta-que-no-es-la-del-servidor"
token_ajeno = jwt.encode({"sub": "1", "rol": "duenio", "exp": 9999999999}, otra_clave, algorithm="HS256")
try:
    leer_token(token_ajeno)
except jwt.InvalidSignatureError:
    print("Rechazado: sin la clave secreta del servidor no se pueden fabricar tokens válidos.")
