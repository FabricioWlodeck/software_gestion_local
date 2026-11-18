"""
Compras (regla 10): suman stock con movimientos 'compra', actualizan producto.costo_ultimo
y, si el producto está en modo margen, recalculan su precio.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.errores import Conflicto, DatosInvalidos, NoEncontrado
from app.formato import redondear_dinero
from app.models import Compra, CompraDetalle, Usuario
from app.repositories.compras import RepositorioCompras
from app.repositories.productos import RepositorioProductos
from app.repositories.proveedores import RepositorioProveedores
from app.schemas.compra import CompraCrear, CompraOut, ItemCompraOut
from app.services.libro import LibroDeStock, validar_cantidad
from app.services.permisos import obtener_sucursal
from app.services.precios import PrecioPorMargen


def compra_a_dto(compra: Compra) -> CompraOut:
    return CompraOut(
        id=compra.id,
        fecha=compra.fecha,
        proveedor_id=compra.proveedor_id,
        proveedor=compra.proveedor.nombre,
        sucursal_id=compra.sucursal_id,
        usuario=compra.usuario.nombre,
        comprobante=compra.comprobante,
        total=compra.total,
        items=[
            ItemCompraOut(
                producto_id=detalle.producto_id,
                producto=detalle.producto.nombre,
                unidad=detalle.producto.unidad,
                cantidad=detalle.cantidad,
                costo_unitario=detalle.costo_unitario,
                subtotal=detalle.subtotal,
            )
            for detalle in compra.detalles
        ],
    )


class ServicioCompras:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.compras = RepositorioCompras(sesion)
        self.productos = RepositorioProductos(sesion)
        self.proveedores = RepositorioProveedores(sesion)
        self.libro = LibroDeStock(sesion)

    def listar(
        self, sucursal_id: int | None, proveedor_id: int | None, desde: date | None, hasta: date | None
    ) -> list[CompraOut]:
        return [compra_a_dto(compra) for compra in self.compras.listar(sucursal_id, proveedor_id, desde, hasta)]

    def registrar(self, usuario: Usuario, datos: CompraCrear) -> CompraOut:
        proveedor = self.proveedores.obtener(datos.proveedor_id)
        if proveedor is None:
            raise NoEncontrado("el proveedor", datos.proveedor_id)
        if not proveedor.activo:
            raise Conflicto(f"El proveedor {proveedor.nombre} está inactivo")
        sucursal = obtener_sucursal(self.sesion, datos.sucursal_id)

        ids = [item.producto_id for item in datos.items]
        if len(ids) != len(set(ids)):
            raise DatosInvalidos("Cada producto puede aparecer una sola vez en la compra")
        productos = self.productos.obtener_varios(ids)
        lineas = []
        for item in sorted(datos.items, key=lambda item: item.producto_id):
            producto = productos.get(item.producto_id)
            if producto is None:
                raise NoEncontrado("el producto", item.producto_id)
            lineas.append((producto, validar_cantidad(producto, item.cantidad), item.costo_unitario))

        stocks = self.libro.bloquear(sucursal, [producto for producto, _, _ in lineas])

        compra = Compra(
            proveedor_id=proveedor.id, sucursal_id=sucursal.id, usuario_id=usuario.id,
            comprobante=datos.comprobante, total=Decimal("0"),
        )
        for producto, cantidad, costo in lineas:
            compra.detalles.append(
                CompraDetalle(
                    producto_id=producto.id, cantidad=cantidad, costo_unitario=costo,
                    subtotal=redondear_dinero(cantidad * costo),
                )
            )
        compra.total = redondear_dinero(sum((detalle.subtotal for detalle in compra.detalles), Decimal("0")))
        self.compras.agregar(compra)

        for producto, cantidad, costo in lineas:
            self.libro.mover(stocks[producto.id], producto, sucursal, "compra", cantidad, usuario.id,
                             compra_id=compra.id)
            producto.costo_ultimo = costo
            # Con costo 0 (una bonificación) se conserva el precio: precio tiene que ser > 0.
            if producto.modo_precio == "margen" and producto.margen is not None and costo > 0:
                producto.precio = PrecioPorMargen(producto.margen).calcular(costo)

        self.sesion.flush()
        self.sesion.refresh(compra)
        respuesta = compra_a_dto(compra)
        self.sesion.commit()
        return respuesta
