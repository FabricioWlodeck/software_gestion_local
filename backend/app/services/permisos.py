"""
Regla de las sucursales: el empleado solo opera en la suya y la dueña en cualquiera.

- resolver_sucursal: para las operaciones que reciben sucursal_id. El empleado que no lo
  manda usa la suya, y si manda otra recibe 403. La dueña lo tiene que mandar (422).
- verificar_sucursal: para las que actúan sobre algo que ya existe (una venta, una caja).
"""

from sqlalchemy.orm import Session

from app.errores import NoEncontrado, OtraSucursal, SucursalRequerida
from app.models import Sucursal, Usuario
from app.repositories.sucursales import RepositorioSucursales


def es_duenio(usuario: Usuario) -> bool:
    return usuario.rol == "duenio"


def resolver_sucursal_id(usuario: Usuario, sucursal_id: int | None, obligatoria: bool = True) -> int | None:
    if not es_duenio(usuario):
        if sucursal_id is not None and sucursal_id != usuario.sucursal_id:
            raise OtraSucursal()
        return usuario.sucursal_id
    if sucursal_id is None and obligatoria:
        raise SucursalRequerida()
    return sucursal_id


def resolver_sucursal(sesion: Session, usuario: Usuario, sucursal_id: int | None) -> Sucursal:
    """Igual que resolver_sucursal_id, y además devuelve la sucursal (404 si no existe)."""
    sucursal_id = resolver_sucursal_id(usuario, sucursal_id)
    return obtener_sucursal(sesion, sucursal_id)


def obtener_sucursal(sesion: Session, sucursal_id: int) -> Sucursal:
    sucursal = RepositorioSucursales(sesion).obtener(sucursal_id)
    if sucursal is None:
        raise NoEncontrado("la sucursal", sucursal_id)
    return sucursal


def verificar_sucursal(usuario: Usuario, sucursal_id: int) -> None:
    if not es_duenio(usuario) and sucursal_id != usuario.sucursal_id:
        raise OtraSucursal()
