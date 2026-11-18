from pydantic import BaseModel, ConfigDict

from app.schemas.comunes import texto


class SucursalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    activa: bool


class SucursalEditar(BaseModel):
    nombre: texto(60)
