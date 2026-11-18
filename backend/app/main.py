"""
Punto de entrada de la API de Punto Lácteo.

Desarrollo, desde backend/:   fastapi dev app/main.py   → http://127.0.0.1:8000/docs
Las rutas no llevan prefijo: nginx y Vite reenvían /api/* hasta acá quitando el /api.

Todos los errores responden {"detail": "texto en español"} (docs/contrato.md, «Errores»).
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import NOMBRE_APP, VERSION
from app.errores import ErrorDeNegocio
from app.routers import auth, cajas, compras, productos, proveedores, reportes, stock, sucursales, usuarios, ventas

registro = logging.getLogger("punto_lacteo")

app = FastAPI(title=NOMBRE_APP, version=VERSION)
for modulo in (auth, sucursales, usuarios, productos, stock, cajas, ventas, proveedores, compras, reportes):
    app.include_router(modulo.router)


@app.exception_handler(ErrorDeNegocio)
def manejar_error_de_negocio(request: Request, error: ErrorDeNegocio) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if error.codigo == 401 else None
    return JSONResponse(status_code=error.codigo, content={"detail": error.mensaje}, headers=headers)


@app.exception_handler(IntegrityError)
def manejar_error_de_integridad(request: Request, error: IntegrityError) -> JSONResponse:
    """Última defensa: si una regla se escapó del service, la base la rechaza y se responde 409."""
    registro.warning("La base rechazó la operación: %s", error.orig)
    texto = str(error.orig)
    if "Duplicate entry" in texto:
        detalle = "Ya existe un registro con ese valor"
    elif "CONSTRAINT" in texto or "constraint" in texto:
        detalle = "La base de datos rechazó la operación: hay un valor que no cumple las reglas"
    else:
        detalle = "La base de datos rechazó la operación"
    return JSONResponse(status_code=409, content={"detail": detalle})


@app.exception_handler(OperationalError)
def manejar_error_operativo(request: Request, error: OperationalError) -> JSONResponse:
    """Un deadlock (1213) o una espera de bloqueo vencida (1205) se pueden reintentar: 409."""
    codigo = error.orig.args[0] if error.orig is not None and error.orig.args else None
    if codigo in (1205, 1213):
        return JSONResponse(status_code=409, content={"detail": "La base estaba ocupada. Probá de nuevo"})
    registro.error("Error de la base de datos: %s", error.orig)
    return JSONResponse(status_code=503, content={"detail": "No se pudo acceder a la base de datos"})


# Traducción de los errores de validación más comunes de Pydantic.
MENSAJES = {
    "missing": "es obligatorio",
    "greater_than": "tiene que ser mayor que {gt}",
    "greater_than_equal": "tiene que ser mayor o igual que {ge}",
    "less_than": "tiene que ser menor que {lt}",
    "less_than_equal": "tiene que ser menor o igual que {le}",
    "string_too_short": "tiene que tener al menos {min_length} caracteres",
    "string_too_long": "puede tener hasta {max_length} caracteres",
    "too_short": "tiene que tener al menos {min_length} elemento",
    "string_pattern_mismatch": "tiene un formato inválido",
    "decimal_max_places": "admite hasta {decimal_places} decimales",
    "decimal_max_digits": "admite hasta {max_digits} dígitos",
    "decimal_whole_digits": "es demasiado grande",
    "decimal_parsing": "tiene que ser un número",
    "decimal_type": "tiene que ser un número",
    "int_parsing": "tiene que ser un número entero",
    "int_type": "tiene que ser un número entero",
    "int_from_float": "tiene que ser un número entero",
    "bool_parsing": "tiene que ser true o false",
    "bool_type": "tiene que ser true o false",
    "string_type": "tiene que ser un texto",
    "literal_error": "tiene que ser uno de: {expected}",
    "date_parsing": "tiene que ser una fecha AAAA-MM-DD",
    "date_from_datetime_parsing": "tiene que ser una fecha AAAA-MM-DD",
    "date_type": "tiene que ser una fecha AAAA-MM-DD",
    "list_type": "tiene que ser una lista",
    "dict_type": "tiene que ser un objeto",
    "model_attributes_type": "tiene que ser un objeto",
    "extra_forbidden": "no se esperaba este campo",
}


def _traducir(error: dict) -> str:
    if error.get("type") == "json_invalid":
        return "El cuerpo de la petición no es un JSON válido"
    ubicacion = [str(parte) for parte in error.get("loc", ()) if parte not in ("body", "query", "path", "form")]
    campo = ".".join(ubicacion)
    plantilla = MENSAJES.get(error.get("type", ""))
    if plantilla is not None:
        try:
            mensaje = plantilla.format(**(error.get("ctx") or {}))
        except (KeyError, IndexError):
            mensaje = plantilla
    else:
        mensaje = str(error.get("msg", "dato inválido")).removeprefix("Value error, ")
    return f"{campo}: {mensaje}" if campo else mensaje


TRADUCCIONES_HTTP = {"Not Found": "No existe la ruta pedida", "Method Not Allowed": "Método no permitido"}


@app.exception_handler(StarletteHTTPException)
def manejar_error_http(request: Request, error: StarletteHTTPException) -> JSONResponse:
    """Los 404 y 405 de rutas inexistentes vienen en inglés desde Starlette: se traducen."""
    detalle = TRADUCCIONES_HTTP.get(error.detail, error.detail) if isinstance(error.detail, str) else error.detail
    return JSONResponse(status_code=error.status_code, content={"detail": detalle}, headers=error.headers)


@app.exception_handler(RequestValidationError)
def manejar_error_de_validacion(request: Request, error: RequestValidationError) -> JSONResponse:
    detalle = "; ".join(dict.fromkeys(_traducir(e) for e in error.errors()))  # sin repetidos
    return JSONResponse(status_code=422, content={"detail": f"Datos inválidos: {detalle}"})
