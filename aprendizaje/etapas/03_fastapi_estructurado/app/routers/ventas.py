from fastapi import APIRouter, status

from app.dependencies import ServicioVentasDep
from app.schemas.venta import VentaIn, VentaOut

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.post("", status_code=status.HTTP_201_CREATED)
def registrar_venta(venta: VentaIn, servicio: ServicioVentasDep) -> VentaOut:
    return servicio.registrar(venta)


@router.get("")
def listar_ventas(servicio: ServicioVentasDep) -> list[VentaOut]:
    return servicio.listar()
