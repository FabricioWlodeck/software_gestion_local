"""
Dependencias. Respecto de la etapa 05, el token fijo se reemplaza por dos guardias:

- obtener_usuario_actual: lee el token Bearer, verifica su firma y su vencimiento,
  y busca al usuario. Si algo falla, responde 401 («no sé quién sos»).
- requerir_rol: además exige un rol. Si no lo tiene, responde 403 («sé quién sos y no podés»).
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.models import Usuario
from app.seguridad import leer_token
from app.services.auth import ServicioAuth
from app.services.productos import ServicioProductos
from app.services.ventas import ServicioVentas

SesionDep = Annotated[Session, Depends(obtener_sesion)]

# Lee el header «Authorization: Bearer <token>». tokenUrl le indica a /docs dónde iniciar sesión.
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")


def obtener_usuario_actual(token: Annotated[str, Depends(esquema_oauth2)], sesion: SesionDep) -> Usuario:
    no_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o vencido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        contenido = leer_token(token)
    except jwt.InvalidTokenError:
        raise no_autenticado
    usuario = sesion.get(Usuario, int(contenido["sub"]))
    if usuario is None:
        raise no_autenticado
    return usuario


UsuarioActualDep = Annotated[Usuario, Depends(obtener_usuario_actual)]


def requerir_rol(*roles: str):
    """Fabrica una dependencia que deja pasar solo a los roles indicados."""
    def verificar_rol(usuario: UsuarioActualDep) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenés permiso para esta acción")
        return usuario
    return verificar_rol


SoloDuenioDep = Annotated[Usuario, Depends(requerir_rol("duenio"))]


def obtener_servicio_auth(sesion: SesionDep) -> ServicioAuth:
    return ServicioAuth(sesion)


def obtener_servicio_productos(sesion: SesionDep) -> ServicioProductos:
    return ServicioProductos(sesion)


def obtener_servicio_ventas(sesion: SesionDep) -> ServicioVentas:
    return ServicioVentas(sesion)


ServicioAuthDep = Annotated[ServicioAuth, Depends(obtener_servicio_auth)]
ServicioProductosDep = Annotated[ServicioProductos, Depends(obtener_servicio_productos)]
ServicioVentasDep = Annotated[ServicioVentas, Depends(obtener_servicio_ventas)]
