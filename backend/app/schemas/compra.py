from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.comunes import CantidadPositiva, DineroNoNegativo, texto_opcional
from app.schemas.producto import Unidad


class ItemCompraIn(BaseModel):
    producto_id: int
    cantidad: CantidadPositiva
    costo_unitario: DineroNoNegativo


class CompraCrear(BaseModel):
    proveedor_id: int
    sucursal_id: int
    comprobante: texto_opcional(40) = None
    items: list[ItemCompraIn] = Field(min_length=1)


class ItemCompraOut(BaseModel):
    producto_id: int
    producto: str
    unidad: Unidad
    cantidad: Decimal
    costo_unitario: Decimal
    subtotal: Decimal


class CompraOut(BaseModel):
    id: int
    fecha: datetime
    proveedor_id: int
    proveedor: str
    sucursal_id: int
    usuario: str
    comprobante: str | None
    total: Decimal
    items: list[ItemCompraOut]
