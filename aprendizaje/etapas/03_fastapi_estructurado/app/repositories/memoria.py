"""
Repositorios en memoria.

Guardan y buscan datos, y nada más: no validan reglas del negocio ni saben de HTTP.
En el módulo 05 se reemplazan por repositorios que usan MariaDB, con los mismos
métodos, y el resto de la aplicación no se entera del cambio.
"""

from datetime import datetime
from decimal import Decimal

from app.schemas.producto import ProductoIn, ProductoOut
from app.schemas.venta import ItemVentaOut, VentaOut


class RepositorioProductos:
    def __init__(self):
        self._productos: dict[int, ProductoOut] = {
            1: ProductoOut(id=1, nombre="Queso cremoso", unidad="kg", precio=Decimal("12500.00"), stock=Decimal("2.100")),
            2: ProductoOut(id=2, nombre="Leche entera 1 L", unidad="unidad", precio=Decimal("1450.00"), stock=Decimal("24")),
            3: ProductoOut(id=3, nombre="Salame milán", unidad="kg", precio=Decimal("18900.00"), stock=Decimal("1.500")),
        }
        self._proximo_id = 4

    def listar(self) -> list[ProductoOut]:
        return list(self._productos.values())

    def obtener(self, producto_id: int) -> ProductoOut | None:
        return self._productos.get(producto_id)

    def agregar(self, datos: ProductoIn) -> ProductoOut:
        producto = ProductoOut(id=self._proximo_id, **datos.model_dump())
        self._productos[producto.id] = producto
        self._proximo_id += 1
        return producto

    def descontar_stock(self, producto_id: int, cantidad: Decimal) -> None:
        producto = self._productos[producto_id]
        self._productos[producto_id] = producto.model_copy(update={"stock": producto.stock - cantidad})

    def borrar(self, producto_id: int) -> bool:
        return self._productos.pop(producto_id, None) is not None


class RepositorioVentas:
    def __init__(self):
        self._ventas: list[VentaOut] = []

    def listar(self) -> list[VentaOut]:
        return list(self._ventas)

    def agregar(self, items: list[ItemVentaOut], total: Decimal) -> VentaOut:
        venta = VentaOut(id=len(self._ventas) + 1, fecha=datetime.now(), items=items, total=total)
        self._ventas.append(venta)
        return venta
