from fastapi import APIRouter, Depends, status

from app.dependencies import ServicioProveedoresDep, solo_duenio
from app.schemas.proveedor import ProveedorCrear, ProveedorEditar, ProveedorOut

router = APIRouter(prefix="/proveedores", tags=["proveedores"], dependencies=[Depends(solo_duenio)])


@router.get("")
def listar_proveedores(servicio: ServicioProveedoresDep, incluir_inactivos: bool = False) -> list[ProveedorOut]:
    return servicio.listar(incluir_inactivos)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_proveedor(datos: ProveedorCrear, servicio: ServicioProveedoresDep) -> ProveedorOut:
    return servicio.crear(datos)


@router.patch("/{proveedor_id}")
def editar_proveedor(proveedor_id: int, datos: ProveedorEditar, servicio: ServicioProveedoresDep) -> ProveedorOut:
    return servicio.editar(proveedor_id, datos)
