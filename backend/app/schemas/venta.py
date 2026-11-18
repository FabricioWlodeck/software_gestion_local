from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.comunes import CantidadPositiva, Motivo, MotivoOpcional
from app.schemas.producto import Unidad

MedioPago = Literal["efectivo", "transferencia"]
EstadoVenta = Literal["valida", "observada", "anulada"]


class ItemVentaIn(BaseModel):
    producto_id: int
    cantidad: CantidadPositiva


class VentaCrear(BaseModel):
    sucursal_id: int | None = None
    medio_pago: MedioPago
    items: list[ItemVentaIn] = Field(min_length=1)


class ItemVentaOut(BaseModel):
    producto_id: int
    producto: str
    unidad: Unidad
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal


class VentaOut(BaseModel):
    """usuario, observada_por y resuelta_por son nombres; usuario_id es el id de quien cobró."""

    id: int
    fecha: datetime
    sucursal_id: int
    caja_id: int
    usuario_id: int
    usuario: str
    medio_pago: MedioPago
    total: Decimal
    estado: EstadoVenta
    motivo_observacion: str | None
    observada_por: str | None
    observada_en: datetime | None
    motivo_resolucion: str | None
    resuelta_por: str | None
    resuelta_en: datetime | None
    items: list[ItemVentaOut]


class ObservarIn(BaseModel):
    motivo: Motivo


class ConfirmarIn(BaseModel):
    motivo: MotivoOpcional = None


class AnularIn(BaseModel):
    motivo: Motivo
