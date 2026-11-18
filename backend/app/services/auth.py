from sqlalchemy.orm import Session

from app.errores import CredencialesInvalidas
from app.repositories.usuarios import RepositorioUsuarios
from app.schemas.auth import Token
from app.seguridad import HASH_FICTICIO, crear_token, verificar


class ServicioAuth:
    def __init__(self, sesion: Session):
        self.usuarios = RepositorioUsuarios(sesion)

    def iniciar_sesion(self, nombre_usuario: str, contrasena: str) -> Token:
        usuario = self.usuarios.obtener_por_nombre_usuario(nombre_usuario.strip())
        if usuario is None:
            verificar(contrasena, HASH_FICTICIO)  # tarda lo mismo que una verificación real
            raise CredencialesInvalidas()
        if not verificar(contrasena, usuario.password_hash):
            raise CredencialesInvalidas()
        if not usuario.activo:
            raise CredencialesInvalidas("Tu usuario está desactivado. Consultá con la dueña.")
        return Token(access_token=crear_token(usuario.id, usuario.rol))
