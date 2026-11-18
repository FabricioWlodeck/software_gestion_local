from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Caja, Venta
from app.repositories import rango_de_fechas


@dataclass
class TotalesDeCaja:
    efectivo: Decimal
    transferencia: Decimal
    cantidad: int


class RepositorioCajas:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _con_usuarios(self):
        return select(Caja).options(joinedload(Caja.usuario_apertura), joinedload(Caja.usuario_cierre))

    def abierta(self, sucursal_id: int, bloqueo: str | None = None) -> Caja | None:
        """
        La caja abierta de la sucursal. bloqueo="compartido" (LOCK IN SHARE MODE) lo usan las
        ventas: no se frenan entre sí, pero el cierre (bloqueo exclusivo) espera a que terminen.
        """
        if bloqueo is None:
            consulta = self._con_usuarios()
        else:
            # Sin joins: MariaDB no admite FOR UPDATE OF y bloquearía también las filas de usuario.
            consulta = select(Caja).with_for_update(read=bloqueo == "compartido")
        consulta = consulta.where(Caja.sucursal_id == sucursal_id, Caja.estado == "abierta")
        return self.sesion.scalars(consulta).first()

    def obtener(self, caja_id: int, para_actualizar: bool = False) -> Caja | None:
        if para_actualizar:
            consulta = select(Caja).where(Caja.id == caja_id).with_for_update()
        else:
            consulta = self._con_usuarios().where(Caja.id == caja_id)
        return self.sesion.scalars(consulta).first()

    def agregar(self, caja: Caja) -> Caja:
        self.sesion.add(caja)
        self.sesion.flush()
        return caja

    def totales(self, caja_id: int, bloquear: bool = False) -> TotalesDeCaja:
        """Suma de las ventas no anuladas de la caja, separadas por medio de pago."""
        consulta = select(
            func.coalesce(func.sum(case((Venta.medio_pago == "efectivo", Venta.total), else_=0)), 0),
            func.coalesce(func.sum(case((Venta.medio_pago == "transferencia", Venta.total), else_=0)), 0),
            func.count(Venta.id),
        ).where(Venta.caja_id == caja_id, Venta.estado != "anulada")
        if bloquear:
            # Lectura con bloqueo: ve las ventas confirmadas aunque la transacción haya leído antes.
            consulta = consulta.with_for_update(read=True)
        efectivo, transferencia, cantidad = self.sesion.execute(consulta).one()
        return TotalesDeCaja(Decimal(efectivo), Decimal(transferencia), int(cantidad))

    def listar(self, sucursal_id: int | None, desde: date | None, hasta: date | None) -> list[Caja]:
        consulta = self._con_usuarios()
        if sucursal_id is not None:
            consulta = consulta.where(Caja.sucursal_id == sucursal_id)
        inicio, fin = rango_de_fechas(desde, hasta)
        if inicio is not None:
            consulta = consulta.where(Caja.abierta_en >= inicio)
        if fin is not None:
            consulta = consulta.where(Caja.abierta_en < fin)
        return list(self.sesion.scalars(consulta.order_by(Caja.abierta_en.desc(), Caja.id.desc())))
