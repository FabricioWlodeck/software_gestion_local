"""
Libro de movimientos de stock (decisión 0003, reglas 1 y 2).

Todo cambio de stock pasa por LibroDeStock.mover(): actualiza stock.cantidad, inserta el
movimiento con su saldo_resultante y, si el saldo cruza el mínimo, agrega el aviso.
Quien llama tiene que haber bloqueado antes las filas de stock (RepositorioStock.bloquear)
y confirma la transacción al final.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.errores import CantidadNoEntera, Conflicto
from app.formato import formatear_cantidad, redondear_cantidad
from app.models import MovimientoStock, Producto, Stock, Sucursal
from app.repositories.stock import RepositorioStock
from app.services.avisos import Avisos


def validar_cantidad(producto: Producto, cantidad: Decimal) -> Decimal:
    """Redondea a gramos y exige números enteros en los productos que se venden por unidad."""
    cantidad = redondear_cantidad(cantidad)
    if producto.unidad == "unidad" and cantidad != cantidad.to_integral_value():
        raise CantidadNoEntera(producto.nombre)
    return cantidad


class LibroDeStock:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.stock = RepositorioStock(sesion)
        self.avisos = Avisos(sesion)

    def bloquear(self, sucursal: Sucursal, productos: list[Producto]) -> dict[int, Stock]:
        """Bloquea las filas de stock (en orden de producto_id) y crea las que falten, en cero."""
        filas = self.stock.bloquear(sucursal.id, [producto.id for producto in productos])
        for producto in productos:
            if producto.id not in filas:
                filas[producto.id] = self.stock.crear(producto.id, sucursal.id)
        return filas

    def mover(
        self,
        stock: Stock,
        producto: Producto,
        sucursal: Sucursal,
        tipo: str,
        cantidad: Decimal,
        usuario_id: int,
        motivo: str | None = None,
        venta_id: int | None = None,
        compra_id: int | None = None,
        traspaso_id: int | None = None,
    ) -> MovimientoStock:
        """cantidad lleva el signo: positiva entra, negativa sale."""
        antes = stock.cantidad
        despues = antes + cantidad
        if despues < 0:
            hay = formatear_cantidad(antes, producto.unidad)
            pedido = formatear_cantidad(-cantidad, producto.unidad)
            raise Conflicto(
                f"Stock insuficiente de {producto.nombre} en {sucursal.nombre}: hay {hay} y se pidieron {pedido}"
            )
        stock.cantidad = despues
        movimiento = self.stock.agregar_movimiento(
            MovimientoStock(
                producto_id=producto.id,
                sucursal_id=sucursal.id,
                tipo=tipo,
                cantidad=cantidad,
                saldo_resultante=despues,
                usuario_id=usuario_id,
                motivo=motivo[:200] if motivo else None,
                venta_id=venta_id,
                compra_id=compra_id,
                traspaso_id=traspaso_id,
            )
        )
        # Regla 2: avisa solo cuando cruza el mínimo; si ya estaba por debajo, no se repite.
        if stock.minimo > 0 and antes >= stock.minimo > despues:
            self.avisos.stock_bajo(sucursal, producto, despues, stock.minimo)
        return movimiento
