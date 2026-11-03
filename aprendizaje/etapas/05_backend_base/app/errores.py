"""Errores de las reglas del negocio. Los mismos de la etapa 03, más los usuarios y los borrados."""

from decimal import Decimal


class ErrorDeNegocio(Exception):
    """Base de todos los errores de reglas del negocio."""


class ProductoNoEncontrado(ErrorDeNegocio):
    def __init__(self, producto_id: int):
        super().__init__(f"No existe el producto {producto_id}")


class UsuarioNoEncontrado(ErrorDeNegocio):
    def __init__(self, usuario_id: int):
        super().__init__(f"No existe el usuario {usuario_id}")


class StockInsuficiente(ErrorDeNegocio):
    def __init__(self, nombre: str, disponible: Decimal, pedido: Decimal):
        super().__init__(f"Stock insuficiente de {nombre}: hay {disponible} y se pidieron {pedido}")


class CantidadInvalida(ErrorDeNegocio):
    def __init__(self, nombre: str):
        super().__init__(f"{nombre} se vende por unidad: la cantidad tiene que ser entera")


class ProductoConVentas(ErrorDeNegocio):
    def __init__(self, nombre: str):
        super().__init__(f"{nombre} tiene ventas registradas y no se puede borrar")


class NombreRepetido(ErrorDeNegocio):
    def __init__(self, nombre: str):
        super().__init__(f"Ya existe un producto llamado {nombre}")
