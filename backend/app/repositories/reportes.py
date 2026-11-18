"""Consultas de los reportes. Los totales cuentan solo las ventas 'valida' (regla 6)."""

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Caja, MovimientoStock, Producto, Sucursal, Usuario, Venta, VentaDetalle
from app.repositories import rango_de_fechas


class RepositorioReportes:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _en_rango(self, consulta, columna, desde: date, hasta: date, sucursal_columna, sucursal_id: int | None):
        inicio, fin = rango_de_fechas(desde, hasta)
        consulta = consulta.where(columna >= inicio, columna < fin)
        if sucursal_id is not None:
            consulta = consulta.where(sucursal_columna == sucursal_id)
        return consulta

    def ventas_por_sucursal_y_medio(self, desde: date, hasta: date, sucursal_id: int | None):
        """Filas (sucursal_id, medio_pago, total, cantidad) de las ventas válidas."""
        consulta = (
            select(Venta.sucursal_id, Venta.medio_pago, func.sum(Venta.total), func.count(Venta.id))
            .where(Venta.estado == "valida")
            .group_by(Venta.sucursal_id, Venta.medio_pago)
        )
        consulta = self._en_rango(consulta, Venta.fecha, desde, hasta, Venta.sucursal_id, sucursal_id)
        return self.sesion.execute(consulta).all()

    def contar_por_estado(self, desde: date, hasta: date, sucursal_id: int | None) -> dict[str, int]:
        consulta = select(Venta.estado, func.count(Venta.id)).group_by(Venta.estado)
        consulta = self._en_rango(consulta, Venta.fecha, desde, hasta, Venta.sucursal_id, sucursal_id)
        return {estado: cantidad for estado, cantidad in self.sesion.execute(consulta)}

    def top_productos(self, desde: date, hasta: date, sucursal_id: int | None, limite: int = 10):
        consulta = (
            select(
                Producto.id, Producto.nombre, Producto.unidad,
                func.sum(VentaDetalle.cantidad), func.sum(VentaDetalle.subtotal),
            )
            .join(VentaDetalle, VentaDetalle.producto_id == Producto.id)
            .join(Venta, Venta.id == VentaDetalle.venta_id)
            .where(Venta.estado == "valida")
            .group_by(Producto.id, Producto.nombre, Producto.unidad)
            .order_by(func.sum(VentaDetalle.subtotal).desc(), Producto.nombre)
            .limit(limite)
        )
        consulta = self._en_rango(consulta, Venta.fecha, desde, hasta, Venta.sucursal_id, sucursal_id)
        return self.sesion.execute(consulta).all()

    def mermas_y_ajustes(self, desde: date, hasta: date, sucursal_id: int | None):
        consulta = (
            select(
                MovimientoStock.fecha, MovimientoStock.sucursal_id, Producto.nombre, Producto.unidad,
                MovimientoStock.tipo, MovimientoStock.cantidad, Usuario.nombre, MovimientoStock.motivo,
            )
            .join(Producto, Producto.id == MovimientoStock.producto_id)
            .join(Usuario, Usuario.id == MovimientoStock.usuario_id)
            .where(MovimientoStock.tipo.in_(("merma", "ajuste")))
            .order_by(MovimientoStock.fecha.desc(), MovimientoStock.id.desc())
        )
        consulta = self._en_rango(
            consulta, MovimientoStock.fecha, desde, hasta, MovimientoStock.sucursal_id, sucursal_id
        )
        return self.sesion.execute(consulta).all()

    def diferencias_caja(self, desde: date, hasta: date, sucursal_id: int | None):
        consulta = (
            select(Caja.id, Caja.sucursal_id, Caja.cerrada_en, Caja.diferencia)
            .where(Caja.estado == "cerrada", Caja.diferencia != 0)
            .order_by(Caja.cerrada_en.desc())
        )
        consulta = self._en_rango(consulta, Caja.cerrada_en, desde, hasta, Caja.sucursal_id, sucursal_id)
        return self.sesion.execute(consulta).all()

    def sucursales(self, sucursal_id: int | None) -> list[Sucursal]:
        consulta = select(Sucursal).order_by(Sucursal.id)
        if sucursal_id is not None:
            consulta = consulta.where(Sucursal.id == sucursal_id)
        return list(self.sesion.scalars(consulta))

    def ventas_diarias(self, desde: date, hasta: date, sucursal_id: int | None):
        dia = func.date(Venta.fecha)
        consulta = (
            select(dia, Venta.sucursal_id, func.sum(Venta.total), func.count(Venta.id))
            .where(Venta.estado == "valida")
            .group_by(dia, Venta.sucursal_id)
            .order_by(dia, Venta.sucursal_id)
        )
        consulta = self._en_rango(consulta, Venta.fecha, desde, hasta, Venta.sucursal_id, sucursal_id)
        return self.sesion.execute(consulta).all()


def como_fecha(valor: date | datetime | str) -> date:
    """DATE(fecha) puede volver como date o como texto según el driver."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor))
