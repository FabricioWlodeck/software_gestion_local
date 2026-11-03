from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Producto, Usuario, Venta, VentaDetalle


class RepositorioVentas:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self) -> list[Venta]:
        # selectinload trae las líneas y sus productos en dos consultas extra,
        # en lugar de una consulta por cada venta (el problema "N+1").
        consulta = (
            select(Venta)
            .options(selectinload(Venta.detalles).selectinload(VentaDetalle.producto))
            .order_by(Venta.id)
        )
        return list(self.sesion.scalars(consulta))

    def agregar(self, usuario_id: int, lineas: list[tuple[Producto, Decimal]], total: Decimal) -> Venta:
        venta = Venta(usuario_id=usuario_id, total=total)
        for producto, cantidad in lineas:
            venta.detalles.append(VentaDetalle(producto=producto, cantidad=cantidad, precio_unitario=producto.precio))
        self.sesion.add(venta)
        self.sesion.flush()  # INSERT de la venta y de sus líneas; la base devuelve id y fecha (RETURNING)
        return venta


class RepositorioUsuarios:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def obtener(self, usuario_id: int) -> Usuario | None:
        return self.sesion.get(Usuario, usuario_id)
