from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status

from app.dependencies import ServicioProductosDep, SoloDuenioDep, UsuarioActualDep, solo_duenio
from app.schemas.comunes import Minimos
from app.schemas.producto import ProductoCrear, ProductoDuenio, ProductoEditar, ProductoEmpleado

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("")
def listar_productos(
    servicio: ServicioProductosDep,
    usuario: UsuarioActualDep,
    incluir_inactivos: bool = False,
    buscar: Annotated[str | None, Query(max_length=80)] = None,
) -> list[ProductoDuenio | ProductoEmpleado]:
    """La dueña recibe modo_precio, margen y costo_ultimo; el empleado no (regla 12)."""
    return servicio.listar(usuario, incluir_inactivos, buscar)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCrear, servicio: ServicioProductosDep, duenia: SoloDuenioDep) -> ProductoDuenio:
    return servicio.crear(duenia, datos)


@router.patch("/{producto_id}")
def editar_producto(
    producto_id: int, datos: ProductoEditar, servicio: ServicioProductosDep, duenia: SoloDuenioDep
) -> ProductoDuenio:
    return servicio.editar(duenia, producto_id, datos)


@router.put("/{producto_id}/minimos", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(solo_duenio)])
def fijar_minimos(producto_id: int, minimos: Annotated[Minimos, Body()], servicio: ServicioProductosDep) -> None:
    """Cuerpo: {"<sucursal_id>": "2.000", …}."""
    servicio.fijar_minimos(producto_id, minimos)
