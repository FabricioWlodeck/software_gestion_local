from pydantic import BaseModel, Field

from app.schemas.auth import Rol
from app.schemas.comunes import texto

NombreUsuario = texto(40)
Contrasena = texto(128, minimo=6)


class UsuarioCrear(BaseModel):
    nombre_usuario: NombreUsuario = Field(pattern=r"^\S+$")  # sin espacios
    nombre: texto(80)
    contrasena: Contrasena
    rol: Rol
    sucursal_id: int | None = None


class UsuarioEditar(BaseModel):
    """PATCH: solo cambian los campos enviados. sucursal_id y telegram_id aceptan null."""

    nombre: texto(80) | None = None
    rol: Rol | None = None
    sucursal_id: int | None = None
    activo: bool | None = None
    telegram_id: int | None = None


class ContrasenaIn(BaseModel):
    contrasena: Contrasena
