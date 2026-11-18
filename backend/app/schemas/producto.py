"""
Productos. Hay dos respuestas (regla 12): la de la dueña incluye modo_precio, margen y
costo_ultimo; la del empleado no. No heredan una de la otra para que la respuesta se
valide siempre contra la clase exacta, y la del empleado prohíbe campos extra.
"""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.comunes import DineroNoNegativo, DineroPositivo, Minimos, Porcentaje, texto

Unidad = Literal["kg", "unidad"]
ModoPrecio = Literal["manual", "margen"]


class StockDeSucursal(BaseModel):
    sucursal_id: int
    cantidad: Decimal
    minimo: Decimal


class _ProductoBase(BaseModel):
    id: int
    nombre: str
    unidad: Unidad
    precio: Decimal
    activo: bool


class ProductoEmpleado(_ProductoBase):
    model_config = ConfigDict(extra="forbid")

    stock: list[StockDeSucursal]


class ProductoDuenio(_ProductoBase):
    modo_precio: ModoPrecio
    margen: Decimal | None
    costo_ultimo: Decimal | None
    stock: list[StockDeSucursal]


class ProductoCrear(BaseModel):
    nombre: texto(80)
    unidad: Unidad
    modo_precio: ModoPrecio = "manual"
    margen: Porcentaje | None = None
    costo_ultimo: DineroNoNegativo | None = None
    precio: DineroPositivo | None = None
    minimos: Minimos | None = None


class ProductoEditar(BaseModel):
    """PATCH: solo cambian los campos enviados."""

    nombre: texto(80) | None = None
    unidad: Unidad | None = None
    modo_precio: ModoPrecio | None = None
    margen: Porcentaje | None = None
    costo_ultimo: DineroNoNegativo | None = None
    precio: DineroPositivo | None = None
    minimos: Minimos | None = None
    activo: bool | None = None
