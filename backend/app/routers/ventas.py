from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import ServicioVentasDep, SoloDuenioDep, UsuarioActualDep
from app.schemas.venta import AnularIn, ConfirmarIn, EstadoVenta, ObservarIn, VentaCrear, VentaOut

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.post("", status_code=status.HTTP_201_CREATED)
def registrar_venta(datos: VentaCrear, servicio: ServicioVentasDep, usuario: UsuarioActualDep) -> VentaOut:
    """Cobrar: necesita la caja abierta. La venta queda a nombre del usuario del token."""
    return servicio.registrar(usuario, datos)


@router.get("")
def listar_ventas(
    servicio: ServicioVentasDep,
    usuario: UsuarioActualDep,
    sucursal_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    estado: EstadoVenta | None = None,
    limite: Annotated[int, Query(ge=1, le=1000)] = 200,
) -> list[VentaOut]:
    """De la más nueva a la más vieja. El empleado solo ve las de hoy de su sucursal."""
    return servicio.listar(usuario, sucursal_id, desde, hasta, estado, limite)


@router.get("/{venta_id}")
def obtener_venta(venta_id: int, servicio: ServicioVentasDep, usuario: UsuarioActualDep) -> VentaOut:
    return servicio.obtener(usuario, venta_id)


@router.post("/{venta_id}/observar")
def observar_venta(
    venta_id: int, datos: ObservarIn, servicio: ServicioVentasDep, usuario: UsuarioActualDep
) -> VentaOut:
    return servicio.observar(usuario, venta_id, datos.motivo)


@router.post("/{venta_id}/confirmar")
def confirmar_venta(
    venta_id: int, servicio: ServicioVentasDep, duenia: SoloDuenioDep, datos: ConfirmarIn | None = None
) -> VentaOut:
    """El cuerpo es opcional: {"motivo": "…"} o nada."""
    return servicio.confirmar(duenia, venta_id, datos.motivo if datos else None)


@router.post("/{venta_id}/anular")
def anular_venta(venta_id: int, datos: AnularIn, servicio: ServicioVentasDep, duenia: SoloDuenioDep) -> VentaOut:
    return servicio.anular(duenia, venta_id, datos.motivo)
