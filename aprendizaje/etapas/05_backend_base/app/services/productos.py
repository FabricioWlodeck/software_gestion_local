from sqlalchemy.orm import Session

from app.errores import NombreRepetido, ProductoConVentas, ProductoNoEncontrado
from app.repositories.productos import RepositorioProductos
from app.schemas.producto import ProductoIn, ProductoOut, Unidad


class ServicioProductos:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.productos = RepositorioProductos(sesion)

    def listar(self, unidad: Unidad | None = None) -> list[ProductoOut]:
        productos = self.productos.listar()
        if unidad is not None:
            productos = [producto for producto in productos if producto.unidad == unidad]
        return [ProductoOut.model_validate(producto) for producto in productos]

    def obtener(self, producto_id: int) -> ProductoOut:
        producto = self.productos.obtener(producto_id)
        if producto is None:
            raise ProductoNoEncontrado(producto_id)
        return ProductoOut.model_validate(producto)

    def crear(self, datos: ProductoIn) -> ProductoOut:
        if self.productos.existe_nombre(datos.nombre):
            raise NombreRepetido(datos.nombre)
        producto = self.productos.agregar(datos)
        self.sesion.commit()
        return ProductoOut.model_validate(producto)

    def borrar(self, producto_id: int) -> None:
        producto = self.productos.obtener(producto_id)
        if producto is None:
            raise ProductoNoEncontrado(producto_id)
        if self.productos.tiene_ventas(producto_id):
            raise ProductoConVentas(producto.nombre)
        self.productos.borrar(producto)
        self.sesion.commit()
