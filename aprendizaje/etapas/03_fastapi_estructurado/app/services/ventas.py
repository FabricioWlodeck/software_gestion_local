from decimal import ROUND_HALF_UP, Decimal

from app.errores import CantidadInvalida, ProductoNoEncontrado, StockInsuficiente
from app.repositories.memoria import RepositorioProductos, RepositorioVentas
from app.schemas.venta import ItemVentaOut, VentaIn, VentaOut

CENTAVOS = Decimal("0.01")


class ServicioVentas:
    def __init__(self, productos: RepositorioProductos, ventas: RepositorioVentas):
        self.productos = productos
        self.ventas = ventas

    def registrar(self, venta: VentaIn) -> VentaOut:
        # 1. Se validan todas las líneas antes de modificar nada.
        lineas: list[ItemVentaOut] = []
        for item in venta.items:
            producto = self.productos.obtener(item.producto_id)
            if producto is None:
                raise ProductoNoEncontrado(item.producto_id)
            if producto.unidad == "unidad" and item.cantidad != item.cantidad.to_integral_value():
                raise CantidadInvalida(producto.nombre)
            if producto.stock < item.cantidad:
                raise StockInsuficiente(producto.nombre, producto.stock, item.cantidad)
            subtotal = (item.cantidad * producto.precio).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
            lineas.append(ItemVentaOut(
                producto_id=producto.id,
                nombre=producto.nombre,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal,
            ))

        # 2. Si todo es válido, se aplican los cambios.
        for linea in lineas:
            self.productos.descontar_stock(linea.producto_id, linea.cantidad)
        total = sum((linea.subtotal for linea in lineas), Decimal("0"))
        return self.ventas.agregar(lineas, total)

    def listar(self) -> list[VentaOut]:
        return self.ventas.listar()
