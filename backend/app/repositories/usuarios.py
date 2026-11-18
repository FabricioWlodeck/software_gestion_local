from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models import Usuario


class RepositorioUsuarios:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def obtener(self, usuario_id: int) -> Usuario | None:
        return self.sesion.get(Usuario, usuario_id)

    def obtener_por_nombre_usuario(self, nombre_usuario: str) -> Usuario | None:
        return self.sesion.scalars(select(Usuario).where(Usuario.nombre_usuario == nombre_usuario)).first()

    def listar(self) -> list[Usuario]:
        return list(self.sesion.scalars(select(Usuario).order_by(Usuario.id)))

    def existe_nombre_usuario(self, nombre_usuario: str) -> bool:
        return self.sesion.scalar(select(exists().where(Usuario.nombre_usuario == nombre_usuario)))

    def existe_telegram_id(self, telegram_id: int, salvo_usuario_id: int) -> bool:
        consulta = exists().where(Usuario.telegram_id == telegram_id, Usuario.id != salvo_usuario_id)
        return self.sesion.scalar(select(consulta))

    def agregar(self, usuario: Usuario) -> Usuario:
        self.sesion.add(usuario)
        self.sesion.flush()  # envía el INSERT ahora para conocer el id
        return usuario
