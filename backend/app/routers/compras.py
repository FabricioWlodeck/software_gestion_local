from datetime import date

from fastapi import APIRouter, Depends, status

from app.dependencies import ServicioComprasDep, SoloDuenioDep, solo_duenio
from app.schemas.compra import CompraCrear, CompraOut

router = APIRouter(prefix="/compras", tags=["compras"], dependencies=[Depends(solo_duenio)])


@router.get("")
def listar_compras(
    servicio: ServicioComprasDep,
    sucursal_id: int | None = None,
    proveedor_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> list[CompraOut]:
    return servicio.listar(sucursal_id, proveedor_id, desde, hasta)


@router.post("", status_code=status.HTTP_201_CREATED)
def registrar_compra(datos: CompraCrear, servicio: ServicioComprasDep, duenia: SoloDuenioDep) -> CompraOut:
    return servicio.registrar(duenia, datos)
