"""
Punto de entrada. Igual que en la etapa 03, más un manejador para los errores
que detecta la propia base de datos (restricciones UNIQUE, CHECK o FOREIGN KEY).

Ejecutar desde la carpeta de la etapa:  fastapi dev app/main.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import NOMBRE_APP, VERSION
from app.errores import (
    CantidadInvalida,
    ErrorDeNegocio,
    NombreRepetido,
    ProductoConVentas,
    ProductoNoEncontrado,
    StockInsuficiente,
    UsuarioNoEncontrado,
)
from app.routers import productos, ventas

app = FastAPI(title=NOMBRE_APP, version=VERSION)
app.include_router(productos.router)
app.include_router(ventas.router)

CODIGOS_HTTP = {
    ProductoNoEncontrado: 404,
    UsuarioNoEncontrado: 404,
    StockInsuficiente: 409,
    ProductoConVentas: 409,
    NombreRepetido: 409,
    CantidadInvalida: 422,
}


@app.exception_handler(ErrorDeNegocio)
def manejar_error_de_negocio(request: Request, error: ErrorDeNegocio) -> JSONResponse:
    codigo = CODIGOS_HTTP.get(type(error), 400)
    return JSONResponse(status_code=codigo, content={"detail": str(error)})


@app.exception_handler(IntegrityError)
def manejar_error_de_integridad(request: Request, error: IntegrityError) -> JSONResponse:
    """Última defensa: si una regla se escapó del service, la base la rechaza y se responde 409."""
    return JSONResponse(status_code=409, content={"detail": f"La base rechazó la operación: {error.orig}"})
