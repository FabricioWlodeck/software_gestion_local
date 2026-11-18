from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import MovimientoStock, Producto, Stock
from app.repositories import rango_de_fechas


class RepositorioStock:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def bloquear(self, sucursal_id: int, producto_ids: list[int]) -> dict[int, Stock]:
        """
        SELECT … FOR UPDATE de las filas de stock de una sucursal, en orden de producto_id.
        Si dos operaciones bloquean siempre en el mismo orden, no pueden esperarse
        mutuamente para siempre (deadlock). Una lectura con bloqueo además ve el último
        valor confirmado, aunque la transacción haya leído antes.
        """
        consulta = (
            select(Stock)
            .where(Stock.sucursal_id == sucursal_id, Stock.producto_id.in_(sorted(producto_ids)))
            .order_by(Stock.producto_id)
            .with_for_update()
        )
        return {stock.producto_id: stock for stock in self.sesion.scalars(consulta)}

    def bloquear_en_sucursales(self, producto_id: int, sucursal_ids: list[int]) -> dict[int, Stock]:
        """Para los traspasos: el mismo producto en dos sucursales, en orden de sucursal_id."""
        consulta = (
            select(Stock)
            .where(Stock.producto_id == producto_id, Stock.sucursal_id.in_(sorted(sucursal_ids)))
            .order_by(Stock.sucursal_id)
            .with_for_update()
        )
        return {stock.sucursal_id: stock for stock in self.sesion.scalars(consulta)}

    def crear(self, producto_id: int, sucursal_id: int, minimo=None) -> Stock:
        stock = Stock(producto_id=producto_id, sucursal_id=sucursal_id)
        if minimo is not None:
            stock.minimo = minimo
        self.sesion.add(stock)
        self.sesion.flush()
        return stock

    def listar_de_sucursal(self, sucursal_id: int) -> list[tuple[Producto, Stock]]:
        consulta = (
            select(Producto, Stock)
            .join(Stock, Stock.producto_id == Producto.id)
            .where(Stock.sucursal_id == sucursal_id, Producto.activo.is_(True))
            .order_by(Producto.nombre)
        )
        return [(producto, stock) for producto, stock in self.sesion.execute(consulta)]

    def agregar_movimiento(self, movimiento: MovimientoStock) -> MovimientoStock:
        self.sesion.add(movimiento)
        return movimiento

    def listar_movimientos(
        self,
        sucursal_id: int | None,
        producto_id: int | None,
        tipo: str | None,
        desde: date | None,
        hasta: date | None,
        limite: int,
        tipos: tuple[str, ...] | None = None,
    ) -> list[MovimientoStock]:
        consulta = select(MovimientoStock).options(
            joinedload(MovimientoStock.producto), joinedload(MovimientoStock.usuario)
        )
        if sucursal_id is not None:
            consulta = consulta.where(MovimientoStock.sucursal_id == sucursal_id)
        if producto_id is not None:
            consulta = consulta.where(MovimientoStock.producto_id == producto_id)
        if tipo is not None:
            consulta = consulta.where(MovimientoStock.tipo == tipo)
        if tipos is not None:
            consulta = consulta.where(MovimientoStock.tipo.in_(tipos))
        inicio, fin = rango_de_fechas(desde, hasta)
        if inicio is not None:
            consulta = consulta.where(MovimientoStock.fecha >= inicio)
        if fin is not None:
            consulta = consulta.where(MovimientoStock.fecha < fin)
        consulta = consulta.order_by(MovimientoStock.fecha.desc(), MovimientoStock.id.desc()).limit(limite)
        return list(self.sesion.scalars(consulta))
