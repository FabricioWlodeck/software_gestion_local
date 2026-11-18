from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models import Sucursal


class RepositorioSucursales:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self) -> list[Sucursal]:
        return list(self.sesion.scalars(select(Sucursal).order_by(Sucursal.id)))

    def obtener(self, sucursal_id: int) -> Sucursal | None:
        return self.sesion.get(Sucursal, sucursal_id)

    def obtener_para_actualizar(self, sucursal_id: int) -> Sucursal | None:
        """SELECT … FOR UPDATE: serializa las operaciones de una sucursal (por ejemplo, abrir la caja)."""
        consulta = select(Sucursal).where(Sucursal.id == sucursal_id).with_for_update()
        return self.sesion.scalars(consulta).first()

    def existe_nombre(self, nombre: str, salvo_id: int) -> bool:
        return self.sesion.scalar(select(exists().where(Sucursal.nombre == nombre, Sucursal.id != salvo_id)))
