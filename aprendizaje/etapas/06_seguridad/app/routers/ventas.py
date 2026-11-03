from fastapi import APIRouter, status

from app.dependencies import ServicioVentasDep, SoloDuenioDep, UsuarioActualDep
from app.schemas.venta import VentaIn, VentaOut

router = APIRouter(prefix="/ventas", tags=["ventas"])


# Cobrar: cualquier usuario identificado. La venta queda a su nombre, según el token.
@router.post("", status_code=status.HTTP_201_CREATED)
def registrar_venta(venta: VentaIn, servicio: ServicioVentasDep, usuario: UsuarioActualDep) -> VentaOut:
    return servicio.registrar(venta, usuario.id)


# Ver todas las ventas (métricas del negocio): solo el rol dueño.
@router.get("")
def listar_ventas(servicio: ServicioVentasDep, duenio: SoloDuenioDep) -> list[VentaOut]:
    return servicio.listar()
