from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, model_validator

from app.schemas.comunes import Cantidad, CantidadPositiva, Motivo, MotivoOpcional
from app.schemas.producto import Unidad

TipoMovimiento = Literal["compra", "venta", "merma", "ajuste", "traspaso_salida", "traspaso_entrada", "anulacion"]


class StockItem(BaseModel):
    producto_id: int
    nombre: str
    unidad: Unidad
    precio: Decimal
    cantidad: Decimal
    minimo: Decimal
    bajo_minimo: bool


class MovimientoOut(BaseModel):
    id: int
    fecha: datetime
    producto_id: int
    producto: str
    unidad: Unidad
    sucursal_id: int
    tipo: TipoMovimiento
    cantidad: Decimal
    saldo_resultante: Decimal
    usuario: str
    motivo: str | None
    venta_id: int | None
    compra_id: int | None
    traspaso_id: int | None


class MovimientoCrear(BaseModel):
    """Merma (cantidad positiva, se guarda negativa) o ajuste (con signo, distinto de cero)."""

    sucursal_id: int | None = None
    producto_id: int
    tipo: Literal["merma", "ajuste"]
    cantidad: Cantidad
    motivo: Motivo

    @model_validator(mode="after")
    def validar_cantidad(self) -> "MovimientoCrear":
        if self.tipo == "merma" and self.cantidad <= 0:
            raise ValueError("La merma se informa con una cantidad positiva")
        if self.tipo == "ajuste" and self.cantidad == 0:
            raise ValueError("El ajuste tiene que tener una cantidad distinta de cero")
        return self


class TraspasoCrear(BaseModel):
    producto_id: int
    origen_id: int
    destino_id: int
    cantidad: CantidadPositiva
    motivo: MotivoOpcional = None

    @model_validator(mode="after")
    def validar_sucursales(self) -> "TraspasoCrear":
        if self.origen_id == self.destino_id:
            raise ValueError("El origen y el destino tienen que ser sucursales distintas")
        return self


class TraspasoOut(BaseModel):
    id: int
    fecha: datetime
    producto_id: int
    producto: str
    unidad: Unidad
    origen_id: int
    destino_id: int
    cantidad: Decimal
    usuario: str
    motivo: str | None
