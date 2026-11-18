from fastapi import APIRouter, Depends

from app.dependencies import ServicioSucursalesDep, obtener_usuario_actual, solo_duenio
from app.schemas.sucursal import SucursalEditar, SucursalOut

router = APIRouter(prefix="/sucursales", tags=["sucursales"], dependencies=[Depends(obtener_usuario_actual)])


@router.get("")
def listar_sucursales(servicio: ServicioSucursalesDep) -> list[SucursalOut]:
    return servicio.listar()


@router.patch("/{sucursal_id}", dependencies=[Depends(solo_duenio)])
def renombrar_sucursal(sucursal_id: int, datos: SucursalEditar, servicio: ServicioSucursalesDep) -> SucursalOut:
    return servicio.renombrar(sucursal_id, datos.nombre)
