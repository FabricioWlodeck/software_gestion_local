from sqlalchemy.orm import Session

from app.errores import Conflicto, DatosInvalidos, NoEncontrado
from app.models import Usuario
from app.repositories.usuarios import RepositorioUsuarios
from app.schemas.auth import UsuarioOut
from app.schemas.usuario import UsuarioCrear, UsuarioEditar
from app.seguridad import hashear
from app.services.permisos import obtener_sucursal


class ServicioUsuarios:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.usuarios = RepositorioUsuarios(sesion)

    def _obtener(self, usuario_id: int) -> Usuario:
        usuario = self.usuarios.obtener(usuario_id)
        if usuario is None:
            raise NoEncontrado("el usuario", usuario_id)
        return usuario

    def _validar_sucursal(self, rol: str, sucursal_id: int | None) -> int | None:
        """El empleado necesita una sucursal; la dueña no tiene (opera en todas)."""
        if rol == "duenio":
            return None
        if sucursal_id is None:
            raise DatosInvalidos("El empleado tiene que pertenecer a una sucursal")
        obtener_sucursal(self.sesion, sucursal_id)
        return sucursal_id

    def listar(self) -> list[UsuarioOut]:
        return [UsuarioOut.model_validate(usuario) for usuario in self.usuarios.listar()]

    def crear(self, datos: UsuarioCrear) -> UsuarioOut:
        if self.usuarios.existe_nombre_usuario(datos.nombre_usuario):
            raise Conflicto(f"Ya existe el usuario {datos.nombre_usuario}")
        usuario = self.usuarios.agregar(
            Usuario(
                nombre_usuario=datos.nombre_usuario,
                nombre=datos.nombre,
                password_hash=hashear(datos.contrasena),
                rol=datos.rol,
                sucursal_id=self._validar_sucursal(datos.rol, datos.sucursal_id),
            )
        )
        self.sesion.commit()
        return UsuarioOut.model_validate(usuario)

    def editar(self, actual: Usuario, usuario_id: int, datos: UsuarioEditar) -> UsuarioOut:
        usuario = self._obtener(usuario_id)
        cambios = datos.model_dump(exclude_unset=True)
        if usuario.id == actual.id:
            if cambios.get("activo") is False:
                raise Conflicto("No podés desactivar tu propio usuario")
            if cambios.get("rol") == "empleado":
                raise Conflicto("No podés quitarte el rol de dueña")
        for campo in ("nombre", "activo"):
            if cambios.get(campo) is not None:
                setattr(usuario, campo, cambios[campo])
        if "telegram_id" in cambios:
            telegram_id = cambios["telegram_id"]
            if telegram_id is not None and self.usuarios.existe_telegram_id(telegram_id, usuario.id):
                raise Conflicto("Ese telegram_id ya está asociado a otro usuario")
            usuario.telegram_id = telegram_id
        if cambios.get("rol") is not None or "sucursal_id" in cambios:
            rol = cambios.get("rol") or usuario.rol
            sucursal_id = cambios["sucursal_id"] if "sucursal_id" in cambios else usuario.sucursal_id
            usuario.sucursal_id = self._validar_sucursal(rol, sucursal_id)
            usuario.rol = rol
        self.sesion.commit()
        return UsuarioOut.model_validate(usuario)

    def cambiar_contrasena(self, usuario_id: int, contrasena: str) -> None:
        usuario = self._obtener(usuario_id)
        usuario.password_hash = hashear(contrasena)
        self.sesion.commit()
