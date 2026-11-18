from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models import Proveedor


class RepositorioProveedores:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self, incluir_inactivos: bool = False) -> list[Proveedor]:
        consulta = select(Proveedor).order_by(Proveedor.nombre)
        if not incluir_inactivos:
            consulta = consulta.where(Proveedor.activo.is_(True))
        return list(self.sesion.scalars(consulta))

    def obtener(self, proveedor_id: int) -> Proveedor | None:
        return self.sesion.get(Proveedor, proveedor_id)

    def existe_nombre(self, nombre: str, salvo_id: int | None = None) -> bool:
        condicion = Proveedor.nombre == nombre
        if salvo_id is not None:
            condicion = condicion & (Proveedor.id != salvo_id)
        return self.sesion.scalar(select(exists().where(condicion)))

    def agregar(self, proveedor: Proveedor) -> Proveedor:
        self.sesion.add(proveedor)
        self.sesion.flush()
        return proveedor
