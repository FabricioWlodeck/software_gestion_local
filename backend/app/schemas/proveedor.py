from pydantic import BaseModel, ConfigDict

from app.schemas.comunes import texto, texto_opcional


class ProveedorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    telefono: str | None
    email: str | None
    notas: str | None
    activo: bool


class ProveedorCrear(BaseModel):
    nombre: texto(80)
    telefono: texto_opcional(40) = None
    email: texto_opcional(120) = None
    notas: texto_opcional(200) = None


class ProveedorEditar(BaseModel):
    """PATCH: solo cambian los campos enviados."""

    nombre: texto(80) | None = None
    telefono: texto_opcional(40) = None
    email: texto_opcional(120) = None
    notas: texto_opcional(200) = None
    activo: bool | None = None
