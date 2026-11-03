"""
Punto de entrada: crea la aplicación, le suma los routers y traduce los errores
del negocio a códigos HTTP. No contiene rutas ni reglas propias.

Ejecutar desde la carpeta de la etapa:  fastapi dev app/main.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import NOMBRE_APP, VERSION
from app.errores import CantidadInvalida, ErrorDeNegocio, ProductoNoEncontrado, StockInsuficiente
from app.routers import productos, ventas

app = FastAPI(title=NOMBRE_APP, version=VERSION)
app.include_router(productos.router)
app.include_router(ventas.router)

# Qué código HTTP corresponde a cada error del negocio.
CODIGOS_HTTP = {
    ProductoNoEncontrado: 404,
    StockInsuficiente: 409,
    CantidadInvalida: 422,
}


@app.exception_handler(ErrorDeNegocio)
def manejar_error_de_negocio(request: Request, error: ErrorDeNegocio) -> JSONResponse:
    codigo = CODIGOS_HTTP.get(type(error), 400)
    return JSONResponse(status_code=codigo, content={"detail": str(error)})
