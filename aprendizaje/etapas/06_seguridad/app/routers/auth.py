from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import ServicioAuthDep, UsuarioActualDep
from app.schemas.auth import Token, UsuarioOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def iniciar_sesion(formulario: Annotated[OAuth2PasswordRequestForm, Depends()], servicio: ServicioAuthDep) -> Token:
    """Recibe usuario y contraseña como formulario (el estándar OAuth2) y devuelve un token."""
    return servicio.iniciar_sesion(formulario.username, formulario.password)


@router.get("/yo")
def quien_soy(usuario: UsuarioActualDep) -> UsuarioOut:
    """Devuelve el usuario del token. El frontend la usa para saber quién inició sesión."""
    return UsuarioOut.model_validate(usuario)
