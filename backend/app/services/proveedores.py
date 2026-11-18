from sqlalchemy.orm import Session

from app.errores import Conflicto, NoEncontrado
from app.models import Proveedor
from app.repositories.proveedores import RepositorioProveedores
from app.schemas.proveedor import ProveedorCrear, ProveedorEditar, ProveedorOut


class ServicioProveedores:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.proveedores = RepositorioProveedores(sesion)

    def listar(self, incluir_inactivos: bool) -> list[ProveedorOut]:
        return [ProveedorOut.model_validate(proveedor) for proveedor in self.proveedores.listar(incluir_inactivos)]

    def crear(self, datos: ProveedorCrear) -> ProveedorOut:
        if self.proveedores.existe_nombre(datos.nombre):
            raise Conflicto(f"Ya existe un proveedor llamado {datos.nombre}")
        proveedor = self.proveedores.agregar(Proveedor(**datos.model_dump()))
        self.sesion.commit()
        return ProveedorOut.model_validate(proveedor)

    def editar(self, proveedor_id: int, datos: ProveedorEditar) -> ProveedorOut:
        proveedor = self.proveedores.obtener(proveedor_id)
        if proveedor is None:
            raise NoEncontrado("el proveedor", proveedor_id)
        cambios = datos.model_dump(exclude_unset=True)
        nombre = cambios.get("nombre")
        if nombre is not None and nombre != proveedor.nombre:
            if self.proveedores.existe_nombre(nombre, salvo_id=proveedor.id):
                raise Conflicto(f"Ya existe un proveedor llamado {nombre}")
            proveedor.nombre = nombre
        for campo in ("telefono", "email", "notas"):  # aceptan null para borrarlos
            if campo in cambios:
                setattr(proveedor, campo, cambios[campo])
        if cambios.get("activo") is not None:
            proveedor.activo = cambios["activo"]
        self.sesion.commit()
        return ProveedorOut.model_validate(proveedor)
