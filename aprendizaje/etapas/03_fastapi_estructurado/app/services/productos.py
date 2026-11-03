from app.errores import ProductoNoEncontrado
from app.repositories.memoria import RepositorioProductos
from app.schemas.producto import ProductoIn, ProductoOut, Unidad


class ServicioProductos:
    def __init__(self, repositorio: RepositorioProductos):
        self.repositorio = repositorio

    def listar(self, unidad: Unidad | None = None) -> list[ProductoOut]:
        productos = self.repositorio.listar()
        if unidad is None:
            return productos
        return [producto for producto in productos if producto.unidad == unidad]

    def obtener(self, producto_id: int) -> ProductoOut:
        producto = self.repositorio.obtener(producto_id)
        if producto is None:
            raise ProductoNoEncontrado(producto_id)
        return producto

    def crear(self, datos: ProductoIn) -> ProductoOut:
        return self.repositorio.agregar(datos)

    def borrar(self, producto_id: int) -> None:
        if not self.repositorio.borrar(producto_id):
            raise ProductoNoEncontrado(producto_id)
