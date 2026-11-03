"""
Dependencias. Respecto de la etapa 03 cambia una sola idea: en lugar de repositorios
únicos en memoria, cada petición recibe una sesión nueva de base de datos, y el service
se construye con esa sesión. Las rutas no cambian.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import TOKEN_DE_PRUEBA
from app.database import obtener_sesion
from app.services.productos import ServicioProductos
from app.services.ventas import ServicioVentas

SesionDep = Annotated[Session, Depends(obtener_sesion)]


def obtener_servicio_productos(sesion: SesionDep) -> ServicioProductos:
    return ServicioProductos(sesion)


def obtener_servicio_ventas(sesion: SesionDep) -> ServicioVentas:
    return ServicioVentas(sesion)


def exigir_token(authorization: Annotated[str | None, Header()] = None) -> None:
    """Corta la petición con 401 si no trae el token. El módulo 06 lo reemplaza por JWT."""
    if authorization != f"Bearer {TOKEN_DE_PRUEBA}":
        raise HTTPException(status_code=401, detail="Falta un token válido", headers={"WWW-Authenticate": "Bearer"})


ServicioProductosDep = Annotated[ServicioProductos, Depends(obtener_servicio_productos)]
ServicioVentasDep = Annotated[ServicioVentas, Depends(obtener_servicio_ventas)]
