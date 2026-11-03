from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

Unidad = Literal["kg", "unidad"]


class ProductoIn(BaseModel):
    """Lo que el cliente envía para crear un producto."""
    nombre: str = Field(min_length=1, max_length=80)
    unidad: Unidad
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: Decimal = Field(ge=0, max_digits=10, decimal_places=3)


class ProductoOut(ProductoIn):
    """Lo que el servidor devuelve: los mismos campos más el id asignado."""
    id: int
