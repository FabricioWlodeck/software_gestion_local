"""
Dependencias: funciones que FastAPI ejecuta antes de cada ruta para entregarle lo que necesita.

Una ruta declara `servicio: ServicioVentasDep` y FastAPI llama a obtener_servicio_ventas(),
que a su vez pide los repositorios. La ruta no sabe cómo se construye el service:
si mañana los repositorios usan MariaDB, solo cambia este archivo.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException

from app.config import TOKEN_DE_PRUEBA
from app.repositories.memoria import RepositorioProductos, RepositorioVentas
from app.services.productos import ServicioProductos
from app.services.ventas import ServicioVentas

# Una sola instancia de cada repositorio mientras viva el proceso, porque los datos están en memoria.
_repositorio_productos = RepositorioProductos()
_repositorio_ventas = RepositorioVentas()


def obtener_servicio_productos() -> ServicioProductos:
    return ServicioProductos(_repositorio_productos)


def obtener_servicio_ventas() -> ServicioVentas:
    return ServicioVentas(_repositorio_productos, _repositorio_ventas)


def exigir_token(authorization: Annotated[str | None, Header()] = None) -> None:
    """Corta la petición con 401 si no trae el token. Se reutiliza en cualquier ruta."""
    if authorization != f"Bearer {TOKEN_DE_PRUEBA}":
        raise HTTPException(status_code=401, detail="Falta un token válido", headers={"WWW-Authenticate": "Bearer"})


# Atajos para anotar parámetros: "este parámetro lo provee tal dependencia".
ServicioProductosDep = Annotated[ServicioProductos, Depends(obtener_servicio_productos)]
ServicioVentasDep = Annotated[ServicioVentas, Depends(obtener_servicio_ventas)]
