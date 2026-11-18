from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.comunes import DineroNoNegativo, texto_opcional


class CajaOut(BaseModel):
    """abierta_por y cerrada_por son los nombres de los usuarios, no sus id."""

    id: int
    sucursal_id: int
    estado: Literal["abierta", "cerrada"]
    abierta_por: str
    abierta_en: datetime
    fondo_inicial: Decimal
    cerrada_por: str | None
    cerrada_en: datetime | None
    efectivo_esperado: Decimal | None
    efectivo_contado: Decimal | None
    diferencia: Decimal | None
    observacion: str | None


class CajaActual(CajaOut):
    """La caja abierta más el resumen en vivo de sus ventas no anuladas."""

    ventas_efectivo: Decimal
    ventas_transferencia: Decimal
    cantidad_ventas: int
    efectivo_esperado_actual: Decimal


class CajaAbrir(BaseModel):
    sucursal_id: int | None = None
    fondo_inicial: DineroNoNegativo


class CajaCerrar(BaseModel):
    efectivo_contado: DineroNoNegativo
    observacion: texto_opcional(200) = None
