"""
Punto de entrada. Igual que en la etapa 05, más el router de autenticación
y el código 401 para las credenciales inválidas.

Ejecutar desde la carpeta de la etapa:  fastapi dev app/main.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import NOMBRE_APP, VERSION
from app.errores import (
    CantidadInvalida,
    CredencialesInvalidas,
    ErrorDeNegocio,
    NombreRepetido,
    ProductoConVentas,
    ProductoNoEncontrado,
    StockInsuficiente,
    UsuarioNoEncontrado,
)
from app.routers import auth, productos, ventas

app = FastAPI(title=NOMBRE_APP, version=VERSION)
app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(ventas.router)

CODIGOS_HTTP = {
    CredencialesInvalidas: 401,
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
    headers = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
    return JSONResponse(status_code=codigo, content={"detail": str(error)}, headers=headers)


@app.exception_handler(IntegrityError)
def manejar_error_de_integridad(request: Request, error: IntegrityError) -> JSONResponse:
    """Última defensa: si una regla se escapó del service, la base la rechaza y se responde 409."""
    return JSONResponse(status_code=409, content={"detail": f"La base rechazó la operación: {error.orig}"})
