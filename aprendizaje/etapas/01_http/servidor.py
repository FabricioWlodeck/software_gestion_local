"""
Etapa 01 - Un servidor HTTP escrito "a mano" con la biblioteca estándar de Python.

Objetivo didáctico: ver qué llega y qué sale por HTTP sin ningún framework.
Todo lo que este archivo hace a mano (separar rutas, leer JSON, validar y
armar respuestas) es lo que FastAPI automatiza en la etapa 02.

Ejecutar:  python servidor.py
Probar:    python cliente.py      (en otra terminal)
"""

import json
import re
from decimal import Decimal, InvalidOperation
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"  # dirección de "esta misma máquina" (localhost)
PUERTO = 8000

# Token fijo SOLO para mostrar cómo viaja el header Authorization.
# No es seguridad real: en el módulo 06 se reemplaza por un JWT firmado.
TOKEN_DE_PRUEBA = "token-de-prueba-123"

UNIDADES_VALIDAS = {"kg", "unidad"}

# "Base de datos" en memoria: un diccionario que se pierde al cerrar el servidor.
# En los módulos 04 y 05 se reemplaza por MariaDB.
# El precio viaja como texto ("12500.00") para no perder precisión: ver módulo 01, sección 2.
productos = {
    1: {"id": 1, "nombre": "Queso cremoso", "unidad": "kg", "precio": "12500.00"},
    2: {"id": 2, "nombre": "Leche entera 1 L", "unidad": "unidad", "precio": "1450.00"},
    3: {"id": 3, "nombre": "Salame milán", "unidad": "kg", "precio": "18900.00"},
}
proximo_id = 4

# Ruta con parámetro: /productos/<número>
RUTA_PRODUCTO = re.compile(r"^/productos/(\d+)$")


def validar_producto(datos):
    """Devuelve la lista de errores encontrados; vacía si los datos son válidos."""
    if not isinstance(datos, dict):
        return ["el cuerpo debe ser un objeto JSON"]

    errores = []
    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        errores.append("nombre: es obligatorio y no puede estar vacío")
    if datos.get("unidad") not in UNIDADES_VALIDAS:
        errores.append("unidad: debe ser 'kg' o 'unidad'")
    try:
        precio = Decimal(str(datos.get("precio")))
        if not precio.is_finite() or precio <= 0:
            errores.append("precio: debe ser mayor que cero")
    except InvalidOperation:
        errores.append('precio: debe ser un número, por ejemplo "1450.00"')
    return errores


class ManejadorPuntoLacteo(BaseHTTPRequestHandler):
    """Atiende cada petición. Python llama a do_GET, do_POST, etc. según el método."""

    # Por defecto Python responde con HTTP/1.0; se usa la versión actual más común.
    protocol_version = "HTTP/1.1"

    # ---------- Métodos HTTP ----------

    def do_GET(self):
        self._registrar_peticion()

        if self.path == "/productos":
            return self._responder(HTTPStatus.OK, list(productos.values()))

        coincidencia = RUTA_PRODUCTO.match(self.path)
        if coincidencia:
            producto = productos.get(int(coincidencia.group(1)))
            if producto is None:
                return self._responder(HTTPStatus.NOT_FOUND, {"detail": "Producto no encontrado"})
            return self._responder(HTTPStatus.OK, producto)

        self._responder(HTTPStatus.NOT_FOUND, {"detail": "Ruta no encontrada"})

    def do_POST(self):
        global proximo_id
        self._registrar_peticion()

        if self.path != "/productos":
            return self._responder(HTTPStatus.NOT_FOUND, {"detail": "Ruta no encontrada"})

        try:
            datos = json.loads(self.cuerpo)
        except json.JSONDecodeError:
            return self._responder(HTTPStatus.BAD_REQUEST, {"detail": "El cuerpo no es JSON válido"})

        errores = validar_producto(datos)
        if errores:
            return self._responder(HTTPStatus.BAD_REQUEST, {"detail": errores})

        producto = {
            "id": proximo_id,
            "nombre": datos["nombre"].strip(),
            "unidad": datos["unidad"],
            "precio": str(Decimal(str(datos["precio"])).quantize(Decimal("0.01"))),
        }
        productos[producto["id"]] = producto
        proximo_id += 1
        # 201 Created + header Location: dónde quedó el recurso nuevo.
        self._responder(HTTPStatus.CREATED, producto, {"Location": f"/productos/{producto['id']}"})

    def do_DELETE(self):
        self._registrar_peticion()

        coincidencia = RUTA_PRODUCTO.match(self.path)
        if not coincidencia:
            return self._responder(HTTPStatus.NOT_FOUND, {"detail": "Ruta no encontrada"})

        # Primero se verifica quién pide, después si el producto existe.
        autorizacion = self.headers.get("Authorization")
        if autorizacion is None:
            return self._responder(
                HTTPStatus.UNAUTHORIZED,
                {"detail": "Falta el header Authorization: Bearer <token>"},
                {"WWW-Authenticate": "Bearer"},
            )
        if autorizacion != f"Bearer {TOKEN_DE_PRUEBA}":
            return self._responder(
                HTTPStatus.UNAUTHORIZED, {"detail": "Token inválido"}, {"WWW-Authenticate": "Bearer"}
            )

        if productos.pop(int(coincidencia.group(1)), None) is None:
            return self._responder(HTTPStatus.NOT_FOUND, {"detail": "Producto no encontrado"})

        # 204 No Content: salió bien y no hay nada para devolver.
        self._responder(HTTPStatus.NO_CONTENT)

    # ---------- Ayudantes ----------

    def _registrar_peticion(self):
        """Lee el cuerpo (si lo hay) e imprime la petición tal como llegó."""
        largo = int(self.headers.get("Content-Length", 0))
        self.cuerpo = self.rfile.read(largo).decode("utf-8") if largo else ""
        self._imprimir("PETICIÓN RECIBIDA", f"{self.requestline}\n{str(self.headers).rstrip()}", self.cuerpo)

    def _responder(self, codigo, datos=None, headers_extra=None):
        """Arma la respuesta: línea de estado, headers, línea en blanco y cuerpo JSON."""
        cuerpo = b""
        self.send_response(codigo)
        if datos is not None:
            cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
            self.send_header("Content-Type", "application/json; charset=utf-8")
        if codigo != HTTPStatus.NO_CONTENT:  # una respuesta 204 no lleva cuerpo ni Content-Length
            self.send_header("Content-Length", str(len(cuerpo)))
        for nombre, valor in (headers_extra or {}).items():
            self.send_header(nombre, valor)

        # Se imprime antes de enviar: así el registro queda completo antes de que
        # el cliente reciba la respuesta y mande la petición siguiente.
        self._imprimir("RESPUESTA ENVIADA", "\n".join(self._lineas_respuesta), cuerpo.decode("utf-8"))
        self.end_headers()  # agrega la línea en blanco y envía la línea de estado y los headers
        self.wfile.write(cuerpo)

    @staticmethod
    def _imprimir(titulo, encabezado, cuerpo):
        """Imprime un mensaje HTTP completo en una sola llamada para que no se mezcle con otros."""
        separador = "=" * 22
        # La línea vacía entre encabezado y cuerpo es la que separa headers y cuerpo en HTTP.
        print(f"{separador} {titulo} {separador}\n{encabezado}\n\n{cuerpo or '(sin cuerpo)'}\n", flush=True)

    # Se extienden dos métodos de la clase base para registrar lo que se envía.
    def send_response_only(self, code, message=None):
        super().send_response_only(code, message)
        self._lineas_respuesta = [f"{self.protocol_version} {code} {message or HTTPStatus(code).phrase}"]

    def send_header(self, keyword, value):
        super().send_header(keyword, value)
        self._lineas_respuesta.append(f"{keyword}: {value}")

    def log_message(self, formato, *args):
        pass  # se reemplaza el registro estándar por las impresiones detalladas de arriba


if __name__ == "__main__":
    servidor = ThreadingHTTPServer((HOST, PUERTO), ManejadorPuntoLacteo)
    print(f"Servidor escuchando en http://{HOST}:{PUERTO}  (Ctrl+C para detener)\n")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
