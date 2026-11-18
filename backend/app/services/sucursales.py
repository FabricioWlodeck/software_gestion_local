from sqlalchemy.orm import Session

from app.errores import Conflicto
from app.repositories.sucursales import RepositorioSucursales
from app.schemas.sucursal import SucursalOut
from app.services.permisos import obtener_sucursal


class ServicioSucursales:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.sucursales = RepositorioSucursales(sesion)

    def listar(self) -> list[SucursalOut]:
        return [SucursalOut.model_validate(sucursal) for sucursal in self.sucursales.listar()]

    def renombrar(self, sucursal_id: int, nombre: str) -> SucursalOut:
        sucursal = obtener_sucursal(self.sesion, sucursal_id)
        if self.sucursales.existe_nombre(nombre, sucursal_id):
            raise Conflicto(f"Ya existe una sucursal llamada {nombre}")
        sucursal.nombre = nombre
        self.sesion.commit()
        return SucursalOut.model_validate(sucursal)
