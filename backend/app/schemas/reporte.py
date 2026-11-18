from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.producto import Unidad


class TotalesPorMedio(BaseModel):
    efectivo: Decimal
    transferencia: Decimal


class TotalSucursal(BaseModel):
    sucursal_id: int
    nombre: str
    total: Decimal
    cantidad_ventas: int


class TopProducto(BaseModel):
    producto_id: int
    nombre: str
    unidad: Unidad
    cantidad: Decimal
    total: Decimal


class MermaOAjuste(BaseModel):
    fecha: datetime
    sucursal_id: int
    producto: str
    unidad: Unidad
    tipo: Literal["merma", "ajuste"]
    cantidad: Decimal
    usuario: str
    motivo: str | None


class DiferenciaCaja(BaseModel):
    caja_id: int
    sucursal_id: int
    cerrada_en: datetime
    diferencia: Decimal


class Resumen(BaseModel):
    """Solo las ventas 'valida' cuentan para los totales (regla 6)."""

    desde: date
    hasta: date
    total: Decimal
    cantidad_ventas: int
    por_medio: TotalesPorMedio
    por_sucursal: list[TotalSucursal]
    top_productos: list[TopProducto]
    ventas_observadas: int
    ventas_anuladas: int
    mermas_y_ajustes: list[MermaOAjuste]
    diferencias_caja: list[DiferenciaCaja]


class VentaDiaria(BaseModel):
    fecha: date
    sucursal_id: int
    total: Decimal
    cantidad: int
