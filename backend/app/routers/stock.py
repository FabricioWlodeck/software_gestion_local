from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import ServicioStockDep, SoloDuenioDep, UsuarioActualDep
from app.schemas.stock import MovimientoCrear, MovimientoOut, StockItem, TipoMovimiento, TraspasoCrear, TraspasoOut

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("")
def listar_stock(
    servicio: ServicioStockDep, usuario: UsuarioActualDep, sucursal_id: int | None = None
) -> list[StockItem]:
    """Stock de los productos activos en una sucursal (el empleado, en la suya)."""
    return servicio.listar(usuario, sucursal_id)


@router.get("/movimientos")
def listar_movimientos(
    servicio: ServicioStockDep,
    usuario: UsuarioActualDep,
    sucursal_id: int | None = None,
    producto_id: int | None = None,
    tipo: TipoMovimiento | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    limite: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> list[MovimientoOut]:
    """Del más nuevo al más viejo. La dueña puede omitir sucursal_id para ver las dos."""
    return servicio.movimientos(usuario, sucursal_id, producto_id, tipo, desde, hasta, limite)


@router.post("/movimientos", status_code=status.HTTP_201_CREATED)
def registrar_movimiento(
    datos: MovimientoCrear, servicio: ServicioStockDep, usuario: UsuarioActualDep
) -> MovimientoOut:
    """Merma (cantidad positiva) o ajuste (con signo), con motivo obligatorio."""
    return servicio.registrar_merma_o_ajuste(usuario, datos)


@router.post("/traspasos", status_code=status.HTTP_201_CREATED)
def registrar_traspaso(datos: TraspasoCrear, servicio: ServicioStockDep, duenia: SoloDuenioDep) -> TraspasoOut:
    return servicio.traspasar(duenia, datos)
