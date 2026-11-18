from datetime import date

from fastapi import APIRouter, Depends, status

from app.dependencies import ServicioCajasDep, UsuarioActualDep, solo_duenio
from app.schemas.caja import CajaAbrir, CajaActual, CajaCerrar, CajaOut

router = APIRouter(prefix="/cajas", tags=["cajas"])


@router.get("/actual")
def caja_actual(
    servicio: ServicioCajasDep, usuario: UsuarioActualDep, sucursal_id: int | None = None
) -> CajaActual | None:
    """La caja abierta de la sucursal con el resumen en vivo, o null si está cerrada."""
    return servicio.actual(usuario, sucursal_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def abrir_caja(datos: CajaAbrir, servicio: ServicioCajasDep, usuario: UsuarioActualDep) -> CajaOut:
    return servicio.abrir(usuario, datos)


@router.post("/{caja_id}/cerrar")
def cerrar_caja(caja_id: int, datos: CajaCerrar, servicio: ServicioCajasDep, usuario: UsuarioActualDep) -> CajaOut:
    return servicio.cerrar(usuario, caja_id, datos)


@router.get("", dependencies=[Depends(solo_duenio)])
def listar_cajas(
    servicio: ServicioCajasDep, sucursal_id: int | None = None, desde: date | None = None, hasta: date | None = None
) -> list[CajaOut]:
    return servicio.listar(sucursal_id, desde, hasta)
