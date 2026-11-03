"""
Registro de ventas con una transacción.

Todo lo que pasa entre el primer SELECT y el commit() forma una sola transacción:
si algo falla antes del commit, la sesión se cierra sin confirmar y MariaDB descarta
los cambios (rollback). No puede quedar una venta guardada sin su descuento de stock.
"""

from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.errores import CantidadInvalida, ProductoNoEncontrado, StockInsuficiente, UsuarioNoEncontrado
from app.models import Producto
from app.repositories.productos import RepositorioProductos
from app.repositories.ventas import RepositorioUsuarios, RepositorioVentas
from app.schemas.venta import VentaIn, VentaOut

CENTAVOS = Decimal("0.01")
GRAMOS = Decimal("0.001")  # la misma escala que la columna DECIMAL(10, 3)


class ServicioVentas:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.productos = RepositorioProductos(sesion)
        self.ventas = RepositorioVentas(sesion)
        self.usuarios = RepositorioUsuarios(sesion)

    def registrar(self, venta: VentaIn, usuario_id: int) -> VentaOut:
        """usuario_id ya no viene del cuerpo de la petición: lo pasa el router desde el token."""
        if self.usuarios.obtener(usuario_id) is None:
            raise UsuarioNoEncontrado(usuario_id)

        # Si un producto aparece en varias líneas, se suman (el bug del ejercicio 2 del módulo 03).
        pedidos: dict[int, Decimal] = defaultdict(Decimal)
        for item in venta.items:
            pedidos[item.producto_id] += item.cantidad

        # 1. Bloquear y validar. Los productos se bloquean en orden de id para que dos ventas
        #    simultáneas no se esperen mutuamente para siempre (deadlock).
        lineas: list[tuple[Producto, Decimal]] = []
        for producto_id in sorted(pedidos):
            cantidad = pedidos[producto_id].quantize(GRAMOS)
            producto = self.productos.obtener_para_actualizar(producto_id)
            if producto is None:
                raise ProductoNoEncontrado(producto_id)
            if producto.unidad == "unidad" and cantidad != cantidad.to_integral_value():
                raise CantidadInvalida(producto.nombre)
            if producto.stock < cantidad:
                raise StockInsuficiente(producto.nombre, producto.stock, cantidad)
            lineas.append((producto, cantidad))

        # 2. Escribir: descontar stock y guardar la venta con sus líneas.
        for producto, cantidad in lineas:
            self.productos.descontar_stock(producto, cantidad)
        total = sum(
            ((cantidad * producto.precio).quantize(CENTAVOS, rounding=ROUND_HALF_UP) for producto, cantidad in lineas),
            Decimal("0"),
        )
        nueva = self.ventas.agregar(usuario_id, lineas, total)

        # 3. Confirmar. Recién acá los cambios quedan guardados y se liberan los bloqueos.
        self.sesion.commit()
        return VentaOut.model_validate(nueva)

    def listar(self) -> list[VentaOut]:
        return [VentaOut.model_validate(venta) for venta in self.ventas.listar()]
