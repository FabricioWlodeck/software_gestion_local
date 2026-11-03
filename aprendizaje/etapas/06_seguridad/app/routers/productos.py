from fastapi import APIRouter, Response, status

from app.dependencies import ServicioProductosDep, SoloDuenioDep, UsuarioActualDep
from app.schemas.producto import ProductoIn, ProductoOut, Unidad

router = APIRouter(prefix="/productos", tags=["productos"])


# Ver productos: cualquier usuario que haya iniciado sesión.
@router.get("")
def listar_productos(servicio: ServicioProductosDep, usuario: UsuarioActualDep, unidad: Unidad | None = None) -> list[ProductoOut]:
    return servicio.listar(unidad)


@router.get("/{producto_id}")
def obtener_producto(producto_id: int, servicio: ServicioProductosDep, usuario: UsuarioActualDep) -> ProductoOut:
    return servicio.obtener(producto_id)


# Crear y borrar productos: solo el rol dueño.
@router.post("", status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoIn, servicio: ServicioProductosDep, duenio: SoloDuenioDep, response: Response) -> ProductoOut:
    producto = servicio.crear(datos)
    response.headers["Location"] = f"/productos/{producto.id}"
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_producto(producto_id: int, servicio: ServicioProductosDep, duenio: SoloDuenioDep) -> None:
    servicio.borrar(producto_id)
