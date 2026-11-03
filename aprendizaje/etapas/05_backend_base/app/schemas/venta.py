from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ItemVentaIn(BaseModel):
    """Una línea del pedido: qué producto y cuánto (en kg o en unidades)."""
    producto_id: int
    cantidad: Decimal = Field(gt=0, max_digits=10, decimal_places=3)


class VentaIn(BaseModel):
    """Lo que envía la caja al cobrar. Por ahora la caja dice quién cobra; en el módulo 06 sale del token."""
    usuario_id: int
    items: list[ItemVentaIn] = Field(min_length=1)


class ItemVentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    producto_id: int
    nombre: str
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal


class VentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: datetime
    usuario_id: int
    items: list[ItemVentaOut]
    total: Decimal
