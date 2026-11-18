"""
Dependencias compartidas por los routers.

- obtener_usuario_actual: lee el token Bearer, verifica firma y vencimiento y busca al
  usuario activo. Si algo falla, 401 («no sé quién sos»).
- requerir_rol: además exige un rol. Si no lo tiene, 403 («sé quién sos y no podés»).
- Un service por petición, con la sesión de esa petición.
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
from app.services.cajas import ServicioCajas
from app.services.compras import ServicioCompras
from app.services.productos import ServicioProductos
from app.services.proveedores import ServicioProveedores
from app.services.reportes import ServicioReportes
from app.services.stock import ServicioStock
from app.services.sucursales import ServicioSucursales
from app.services.usuarios import ServicioUsuarios
from app.services.ventas import ServicioVentas

SesionDep = Annotated[Session, Depends(obtener_sesion)]

# Lee el header «Authorization: Bearer <token>». tokenUrl es relativa para que /docs funcione
# también detrás del proxy (/api/docs → /api/auth/token). auto_error=False: el 401 lo armamos
# nosotros, con el mensaje en español.
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


def _no_autenticado(mensaje: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=mensaje, headers={"WWW-Authenticate": "Bearer"}
    )


def obtener_usuario_actual(token: Annotated[str | None, Depends(esquema_oauth2)], sesion: SesionDep) -> Usuario:
    if not token:
        raise _no_autenticado("Iniciá sesión para continuar")
    try:
        contenido = leer_token(token)
        usuario_id = int(contenido["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise _no_autenticado("Tu sesión venció o no es válida. Iniciá sesión de nuevo")
    usuario = sesion.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise _no_autenticado("Tu usuario no existe o está desactivado")
    # Termina la transacción de solo lectura: con REPEATABLE READ, MariaDB toma la «foto» de los
    # datos en la primera lectura, y el service tiene que empezar con una foto nueva.
    sesion.commit()
    return usuario


UsuarioActualDep = Annotated[Usuario, Depends(obtener_usuario_actual)]


def requerir_rol(*roles: str):
    """Fabrica una dependencia que deja pasar solo a los roles indicados."""

    def verificar_rol(usuario: UsuarioActualDep) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenés permiso para esta acción")
        return usuario

    return verificar_rol


solo_duenio = requerir_rol("duenio")  # una sola instancia: FastAPI la ejecuta una vez por petición
SoloDuenioDep = Annotated[Usuario, Depends(solo_duenio)]


def obtener_servicio_auth(sesion: SesionDep) -> ServicioAuth:
    return ServicioAuth(sesion)


def obtener_servicio_sucursales(sesion: SesionDep) -> ServicioSucursales:
    return ServicioSucursales(sesion)


def obtener_servicio_usuarios(sesion: SesionDep) -> ServicioUsuarios:
    return ServicioUsuarios(sesion)


def obtener_servicio_productos(sesion: SesionDep) -> ServicioProductos:
    return ServicioProductos(sesion)


def obtener_servicio_stock(sesion: SesionDep) -> ServicioStock:
    return ServicioStock(sesion)


def obtener_servicio_cajas(sesion: SesionDep) -> ServicioCajas:
    return ServicioCajas(sesion)


def obtener_servicio_ventas(sesion: SesionDep) -> ServicioVentas:
    return ServicioVentas(sesion)


def obtener_servicio_proveedores(sesion: SesionDep) -> ServicioProveedores:
    return ServicioProveedores(sesion)


def obtener_servicio_compras(sesion: SesionDep) -> ServicioCompras:
    return ServicioCompras(sesion)


def obtener_servicio_reportes(sesion: SesionDep) -> ServicioReportes:
    return ServicioReportes(sesion)


ServicioAuthDep = Annotated[ServicioAuth, Depends(obtener_servicio_auth)]
ServicioSucursalesDep = Annotated[ServicioSucursales, Depends(obtener_servicio_sucursales)]
ServicioUsuariosDep = Annotated[ServicioUsuarios, Depends(obtener_servicio_usuarios)]
ServicioProductosDep = Annotated[ServicioProductos, Depends(obtener_servicio_productos)]
ServicioStockDep = Annotated[ServicioStock, Depends(obtener_servicio_stock)]
ServicioCajasDep = Annotated[ServicioCajas, Depends(obtener_servicio_cajas)]
ServicioVentasDep = Annotated[ServicioVentas, Depends(obtener_servicio_ventas)]
ServicioProveedoresDep = Annotated[ServicioProveedores, Depends(obtener_servicio_proveedores)]
ServicioComprasDep = Annotated[ServicioCompras, Depends(obtener_servicio_compras)]
ServicioReportesDep = Annotated[ServicioReportes, Depends(obtener_servicio_reportes)]
