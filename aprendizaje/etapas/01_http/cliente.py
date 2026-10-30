"""
Etapa 01 - Cliente HTTP que recorre los casos del módulo.

Usa http.client (biblioteca estándar) para ver la respuesta tal como llega,
sin la "magia" de librerías como requests. La petición completa, tal como
viaja, se ve en la terminal del servidor.
En el módulo 09 este papel lo cumple fetch() dentro de React.

Ejecutar con el servidor ya levantado:
    python cliente.py              (pausa entre casos)
    python cliente.py --sin-pausa  (todos los casos de corrido)
"""

import http.client
import json
import sys

HOST = "127.0.0.1"
PUERTO = 8000
TOKEN_DE_PRUEBA = "token-de-prueba-123"

# (título, método, ruta, cuerpo JSON o None, headers extra)
CASOS = [
    ("1. Listar productos", "GET", "/productos", None, {}),
    ("2. Pedir un producto que no existe", "GET", "/productos/99", None, {}),
    (
        "3. Crear un producto válido",
        "POST",
        "/productos",
        {"nombre": "Yogur bebible 1 L", "unidad": "unidad", "precio": "2300.00"},
        {},
    ),
    (
        "4. Crear un producto con datos inválidos",
        "POST",
        "/productos",
        {"nombre": "", "unidad": "litro", "precio": "-5"},
        {},
    ),
    ("5. Borrar sin token", "DELETE", "/productos/2", None, {}),
    ("6. Borrar con token Bearer", "DELETE", "/productos/2", None, {"Authorization": f"Bearer {TOKEN_DE_PRUEBA}"}),
    ("7. Listar de nuevo para ver los cambios", "GET", "/productos", None, {}),
]


def enviar(titulo, metodo, ruta, datos, headers_extra):
    headers = {"Accept": "application/json", **headers_extra}
    cuerpo = None
    if datos is not None:
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    conexion = http.client.HTTPConnection(HOST, PUERTO)
    conexion.request(metodo, ruta, body=cuerpo, headers=headers)
    respuesta = conexion.getresponse()
    contenido = respuesta.read().decode("utf-8")
    conexion.close()

    print("=" * 10, titulo, "=" * 10)
    print(f">>> {metodo} {ruta}")
    if cuerpo:
        print(f">>> cuerpo enviado: {cuerpo.decode('utf-8')}")
    print(f"<<< HTTP/{respuesta.version / 10:.1f} {respuesta.status} {respuesta.reason}")
    for nombre, valor in respuesta.getheaders():
        print(f"<<< {nombre}: {valor}")
    print("<<<")
    if contenido:
        print(f"<<< {contenido}")
    print()


if __name__ == "__main__":
    pausar = "--sin-pausa" not in sys.argv
    for caso in CASOS:
        enviar(*caso)
        if pausar:
            input("Enter para el siguiente caso (mirá también la terminal del servidor)...")
            print()
