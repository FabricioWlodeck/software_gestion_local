"""
Patrón Estrategia aplicado al precio de venta (etapa 11 del material de aprendizaje).

La dueña fija el precio a mano o con un margen sobre el último costo de compra.
precio = costo × (1 + margen/100), redondeado a centavos.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.errores import DatosInvalidos
from app.formato import redondear_dinero


class EstrategiaDePrecio(Protocol):
    def calcular(self, costo: Decimal | None) -> Decimal: ...


@dataclass(frozen=True)
class PrecioPorMargen:
    porcentaje: Decimal  # 35 significa 35 % sobre el costo

    def calcular(self, costo: Decimal | None) -> Decimal:
        return redondear_dinero(costo * (1 + self.porcentaje / 100))


@dataclass(frozen=True)
class PrecioManual:
    precio: Decimal

    def calcular(self, costo: Decimal | None) -> Decimal:
        return self.precio  # el costo no influye: la dueña lo fijó a mano


def calcular_precio(
    modo: str, margen: Decimal | None, costo: Decimal | None, precio: Decimal | None
) -> Decimal:
    """
    Regla 11: en modo margen, si hay costo, el precio se calcula; si no hay costo (o es 0),
    hace falta un precio. En modo manual el precio es obligatorio.
    """
    if modo == "margen":
        if margen is None:
            raise DatosInvalidos("Para el modo margen indicá el margen (porcentaje sobre el costo)")
        if costo is not None and costo > 0:
            return PrecioPorMargen(margen).calcular(costo)
    if precio is None:
        raise DatosInvalidos("Indicá el precio de venta")
    return PrecioManual(precio).calcular(costo)
