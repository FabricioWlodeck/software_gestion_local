"""
Patrón Estrategia (Strategy) aplicado al precio de venta.

La dueña fija el precio de dos formas: con un margen sobre el costo de compra o a mano.
Cada forma es una estrategia con la misma interfaz, calcular(costo), y el resto del
sistema no sabe cuál está usando. Agregar una forma nueva es agregar una clase, sin
modificar las que ya existen ni el código que las usa.

Ejecutar desde la carpeta de la etapa:  python backend/precios.py
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

CENTAVOS = Decimal("0.01")


class EstrategiaDePrecio(Protocol):
    """Lo único que el resto del sistema sabe de una estrategia: que tiene calcular()."""

    def calcular(self, costo: Decimal) -> Decimal: ...


@dataclass(frozen=True)
class PrecioPorMargen:
    porcentaje: Decimal  # 35 significa 35 % sobre el costo

    def calcular(self, costo: Decimal) -> Decimal:
        return (costo * (1 + self.porcentaje / 100)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PrecioManual:
    precio: Decimal

    def calcular(self, costo: Decimal) -> Decimal:
        return self.precio  # el costo no influye: la dueña lo fijó a mano


def estrategia_para(modo: str, valor: Decimal) -> EstrategiaDePrecio:
    """Fábrica: traduce lo que guarda la base (dos columnas, modo y valor) a una estrategia."""
    if modo == "margen":
        return PrecioPorMargen(valor)
    if modo == "manual":
        return PrecioManual(valor)
    raise ValueError(f"Modo de precio desconocido: {modo}")


@dataclass
class Producto:
    """Lo mínimo de un producto para este ejemplo; en el sistema real es el modelo de SQLAlchemy."""

    nombre: str
    modo_precio: str
    valor_precio: Decimal
    precio: Decimal


def registrar_costo_nuevo(producto: Producto, costo: Decimal) -> None:
    """Lo que haría el service al cargar una compra: recalcular el precio con la estrategia del producto."""
    estrategia = estrategia_para(producto.modo_precio, producto.valor_precio)
    producto.precio = estrategia.calcular(costo)


if __name__ == "__main__":
    productos = [
        Producto("Queso cremoso", "margen", Decimal("35"), Decimal("12500.00")),
        Producto("Salame milán", "margen", Decimal("40"), Decimal("18900.00")),
        Producto("Leche entera 1 L", "manual", Decimal("1450.00"), Decimal("1450.00")),
    ]
    costos_nuevos = [Decimal("9800.00"), Decimal("14000.00"), Decimal("1180.00")]

    print(f"{'Producto':<18} {'Modo':<12} {'Costo nuevo':>12} {'Precio antes':>13} {'Precio nuevo':>13}")
    for producto, costo in zip(productos, costos_nuevos):
        antes = producto.precio
        registrar_costo_nuevo(producto, costo)
        modo = f"{producto.modo_precio} {producto.valor_precio}" if producto.modo_precio == "margen" else "manual"
        print(f"{producto.nombre:<18} {modo:<12} {costo:>12} {antes:>13} {producto.precio:>13}")
