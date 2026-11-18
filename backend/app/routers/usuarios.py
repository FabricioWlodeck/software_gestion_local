from fastapi import APIRouter, Depends, status

from app.dependencies import ServicioUsuariosDep, SoloDuenioDep, solo_duenio
from app.schemas.auth import UsuarioOut
from app.schemas.usuario import ContrasenaIn, UsuarioCrear, UsuarioEditar

# Todo el router es solo para la dueña.
router = APIRouter(prefix="/usuarios", tags=["usuarios"], dependencies=[Depends(solo_duenio)])


@router.get("")
def listar_usuarios(servicio: ServicioUsuariosDep) -> list[UsuarioOut]:
    return servicio.listar()


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCrear, servicio: ServicioUsuariosDep) -> UsuarioOut:
    return servicio.crear(datos)


@router.patch("/{usuario_id}")
def editar_usuario(
    usuario_id: int, datos: UsuarioEditar, servicio: ServicioUsuariosDep, duenia: SoloDuenioDep
) -> UsuarioOut:
    return servicio.editar(duenia, usuario_id, datos)


@router.put("/{usuario_id}/contrasena", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_contrasena(usuario_id: int, datos: ContrasenaIn, servicio: ServicioUsuariosDep) -> None:
    servicio.cambiar_contrasena(usuario_id, datos.contrasena)
