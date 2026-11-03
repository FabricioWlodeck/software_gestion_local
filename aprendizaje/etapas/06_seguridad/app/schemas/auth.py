from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Respuesta del inicio de sesión, con los nombres de campo que define el estándar OAuth2."""
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    """Datos públicos de un usuario. No incluye password_hash: el modelo de respuesta lo descarta."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    rol: str
