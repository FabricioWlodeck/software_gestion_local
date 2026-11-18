from typing import Literal

from pydantic import BaseModel, ConfigDict

Rol = Literal["duenio", "empleado"]


class Token(BaseModel):
    """Respuesta del inicio de sesión, con los nombres de campo del estándar OAuth2."""

    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    """Datos públicos de un usuario (nunca el hash de la contraseña)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_usuario: str
    nombre: str
    rol: Rol
    sucursal_id: int | None
    activo: bool
    telegram_id: int | None
