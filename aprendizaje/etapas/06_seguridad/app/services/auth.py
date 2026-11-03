from sqlalchemy.orm import Session

from app.errores import CredencialesInvalidas
from app.repositories.ventas import RepositorioUsuarios
from app.schemas.auth import Token
from app.seguridad import HASH_FICTICIO, crear_token, verificar


class ServicioAuth:
    def __init__(self, sesion: Session):
        self.usuarios = RepositorioUsuarios(sesion)

    def iniciar_sesion(self, nombre: str, contrasena: str) -> Token:
        usuario = self.usuarios.obtener_por_nombre(nombre)
        if usuario is None or usuario.password_hash is None:
            verificar(contrasena, HASH_FICTICIO)  # tarda lo mismo que una verificación real
            raise CredencialesInvalidas()
        if not verificar(contrasena, usuario.password_hash):
            raise CredencialesInvalidas()
        return Token(access_token=crear_token(usuario.id, usuario.rol))
