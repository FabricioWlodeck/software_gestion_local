from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from app.models import Producto, Stock


class RepositorioProductos:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self, incluir_inactivos: bool = False, buscar: str | None = None) -> list[Producto]:
        # selectinload trae el stock de todos los productos en una consulta extra (no una por producto).
        consulta = select(Producto).options(selectinload(Producto.stocks)).order_by(Producto.nombre)
        if not incluir_inactivos:
            consulta = consulta.where(Producto.activo.is_(True))
        if buscar:
            # La intercalación de la base no distingue mayúsculas ni tildes: «queso» encuentra «Queso».
            consulta = consulta.where(Producto.nombre.contains(buscar, autoescape=True))
        return list(self.sesion.scalars(consulta))

    def obtener(self, producto_id: int) -> Producto | None:
        return self.sesion.get(Producto, producto_id)

    def obtener_varios(self, producto_ids: list[int]) -> dict[int, Producto]:
        consulta = select(Producto).where(Producto.id.in_(producto_ids))
        return {producto.id: producto for producto in self.sesion.scalars(consulta)}

    def obtener_para_actualizar(self, producto_id: int) -> Producto | None:
        consulta = select(Producto).where(Producto.id == producto_id).with_for_update()
        return self.sesion.scalars(consulta).first()

    def existe_nombre(self, nombre: str, salvo_id: int | None = None) -> bool:
        condicion = Producto.nombre == nombre
        if salvo_id is not None:
            condicion = condicion & (Producto.id != salvo_id)
        return self.sesion.scalar(select(exists().where(condicion)))

    def agregar(self, producto: Producto) -> Producto:
        self.sesion.add(producto)
        self.sesion.flush()
        return producto

    def stock_del_producto(self, producto_id: int) -> list[Stock]:
        consulta = select(Stock).where(Stock.producto_id == producto_id).order_by(Stock.sucursal_id)
        return list(self.sesion.scalars(consulta))
