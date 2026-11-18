from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Compra, CompraDetalle
from app.repositories import rango_de_fechas


class RepositorioCompras:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _completa(self):
        return select(Compra).options(
            joinedload(Compra.proveedor),
            joinedload(Compra.usuario),
            selectinload(Compra.detalles).joinedload(CompraDetalle.producto),
        )

    def obtener(self, compra_id: int) -> Compra | None:
        return self.sesion.scalars(self._completa().where(Compra.id == compra_id)).first()

    def listar(
        self, sucursal_id: int | None, proveedor_id: int | None, desde: date | None, hasta: date | None
    ) -> list[Compra]:
        consulta = self._completa()
        if sucursal_id is not None:
            consulta = consulta.where(Compra.sucursal_id == sucursal_id)
        if proveedor_id is not None:
            consulta = consulta.where(Compra.proveedor_id == proveedor_id)
        inicio, fin = rango_de_fechas(desde, hasta)
        if inicio is not None:
            consulta = consulta.where(Compra.fecha >= inicio)
        if fin is not None:
            consulta = consulta.where(Compra.fecha < fin)
        return list(self.sesion.scalars(consulta.order_by(Compra.fecha.desc(), Compra.id.desc())).unique())

    def agregar(self, compra: Compra) -> Compra:
        self.sesion.add(compra)
        self.sesion.flush()
        return compra
