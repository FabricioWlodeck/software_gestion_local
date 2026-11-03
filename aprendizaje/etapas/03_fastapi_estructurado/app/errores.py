"""
Errores de las reglas del negocio.

No saben nada de HTTP: el service los lanza y main.py decide con qué código
responder a cada uno. Así el mismo service sirve para una API, un script o un bot.
"""

from decimal import Decimal


class ErrorDeNegocio(Exception):
    """Base de todos los errores de reglas del negocio."""


class ProductoNoEncontrado(ErrorDeNegocio):
    def __init__(self, producto_id: int):
        super().__init__(f"No existe el producto {producto_id}")


class StockInsuficiente(ErrorDeNegocio):
    def __init__(self, nombre: str, disponible: Decimal, pedido: Decimal):
        super().__init__(f"Stock insuficiente de {nombre}: hay {disponible} y se pidieron {pedido}")


class CantidadInvalida(ErrorDeNegocio):
    def __init__(self, nombre: str):
        super().__init__(f"{nombre} se vende por unidad: la cantidad tiene que ser entera")
