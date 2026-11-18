from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Venta, VentaDetalle
from app.repositories import rango_de_fechas


class RepositorioVentas:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _completa(self):
        # joinedload para los usuarios (uno por venta) y selectinload para las líneas:
        # pocas consultas aunque haya muchas ventas (se evita el problema N+1).
        return select(Venta).options(
            joinedload(Venta.usuario),
            joinedload(Venta.usuario_observacion),
            joinedload(Venta.usuario_resolucion),
            selectinload(Venta.detalles).joinedload(VentaDetalle.producto),
        )

    def obtener(self, venta_id: int, para_actualizar: bool = False) -> Venta | None:
        if para_actualizar:
            # Sin joins: MariaDB no admite FOR UPDATE OF y bloquearía también las filas unidas.
            # Las relaciones se cargan después, con consultas comunes.
            consulta = select(Venta).where(Venta.id == venta_id).with_for_update()
        else:
            consulta = self._completa().where(Venta.id == venta_id)
        return self.sesion.scalars(consulta).first()

    def listar(
        self,
        sucursal_id: int | None,
        desde: date | None,
        hasta: date | None,
        estado: str | None,
        limite: int,
        solo_hoy: bool = False,
    ) -> list[Venta]:
        consulta = self._completa()
        if sucursal_id is not None:
            consulta = consulta.where(Venta.sucursal_id == sucursal_id)
        if solo_hoy:
            consulta = consulta.where(Venta.fecha >= func.curdate())  # la fecha de hoy según la base
        else:
            inicio, fin = rango_de_fechas(desde, hasta)
            if inicio is not None:
                consulta = consulta.where(Venta.fecha >= inicio)
            if fin is not None:
                consulta = consulta.where(Venta.fecha < fin)
        if estado is not None:
            consulta = consulta.where(Venta.estado == estado)
        consulta = consulta.order_by(Venta.fecha.desc(), Venta.id.desc()).limit(limite)
        return list(self.sesion.scalars(consulta).unique())

    def agregar(self, venta: Venta) -> Venta:
        self.sesion.add(venta)
        self.sesion.flush()  # INSERT de la venta; la base devuelve el id y la fecha
        return venta
