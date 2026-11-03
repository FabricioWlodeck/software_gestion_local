"""
Repositorio de productos con SQLAlchemy.

Tiene los mismos métodos que el repositorio en memoria de la etapa 03, más uno nuevo
(obtener_para_actualizar) que solo tiene sentido con una base compartida.
"""

from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models import Producto, VentaDetalle
from app.schemas.producto import ProductoIn


class RepositorioProductos:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self) -> list[Producto]:
        return list(self.sesion.scalars(select(Producto).order_by(Producto.id)))

    def obtener(self, producto_id: int) -> Producto | None:
        return self.sesion.get(Producto, producto_id)

    def obtener_para_actualizar(self, producto_id: int) -> Producto | None:
        """SELECT ... FOR UPDATE: bloquea la fila hasta el commit para que nadie más la modifique."""
        consulta = select(Producto).where(Producto.id == producto_id).with_for_update()
        return self.sesion.scalars(consulta).first()

    def existe_nombre(self, nombre: str) -> bool:
        return self.sesion.scalar(select(exists().where(Producto.nombre == nombre)))

    def tiene_ventas(self, producto_id: int) -> bool:
        return self.sesion.scalar(select(exists().where(VentaDetalle.producto_id == producto_id)))

    def agregar(self, datos: ProductoIn) -> Producto:
        producto = Producto(**datos.model_dump())
        self.sesion.add(producto)
        self.sesion.flush()  # envía el INSERT ahora, para conocer el id que asigna la base
        return producto

    def descontar_stock(self, producto: Producto, cantidad: Decimal) -> None:
        # No hace falta escribir el UPDATE: la sesión detecta el cambio y lo envía al confirmar.
        producto.stock -= cantidad

    def borrar(self, producto: Producto) -> None:
        self.sesion.delete(producto)
