from fastapi import APIRouter, Depends, Response, status

from app.dependencies import ServicioProductosDep, exigir_token
from app.schemas.producto import ProductoIn, ProductoOut, Unidad

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("")
def listar_productos(servicio: ServicioProductosDep, unidad: Unidad | None = None) -> list[ProductoOut]:
    return servicio.listar(unidad)


@router.get("/{producto_id}")
def obtener_producto(producto_id: int, servicio: ServicioProductosDep) -> ProductoOut:
    return servicio.obtener(producto_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoIn, servicio: ServicioProductosDep, response: Response) -> ProductoOut:
    producto = servicio.crear(datos)
    response.headers["Location"] = f"/productos/{producto.id}"
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(exigir_token)])
def borrar_producto(producto_id: int, servicio: ServicioProductosDep) -> None:
    servicio.borrar(producto_id)
