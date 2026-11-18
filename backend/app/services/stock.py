from datetime import date

from sqlalchemy.orm import Session

from app.errores import NoEncontrado
from app.models import MovimientoStock, Producto, Traspaso, Usuario
from app.repositories.productos import RepositorioProductos
from app.repositories.stock import RepositorioStock
from app.schemas.stock import MovimientoCrear, MovimientoOut, StockItem, TraspasoCrear, TraspasoOut
from app.services.libro import LibroDeStock, validar_cantidad
from app.services.permisos import obtener_sucursal, resolver_sucursal, resolver_sucursal_id


def movimiento_a_dto(movimiento: MovimientoStock) -> MovimientoOut:
    return MovimientoOut(
        id=movimiento.id,
        fecha=movimiento.fecha,
        producto_id=movimiento.producto_id,
        producto=movimiento.producto.nombre,
        unidad=movimiento.producto.unidad,
        sucursal_id=movimiento.sucursal_id,
        tipo=movimiento.tipo,
        cantidad=movimiento.cantidad,
        saldo_resultante=movimiento.saldo_resultante,
        usuario=movimiento.usuario.nombre,
        motivo=movimiento.motivo,
        venta_id=movimiento.venta_id,
        compra_id=movimiento.compra_id,
        traspaso_id=movimiento.traspaso_id,
    )


class ServicioStock:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.stock = RepositorioStock(sesion)
        self.productos = RepositorioProductos(sesion)
        self.libro = LibroDeStock(sesion)

    def _producto(self, producto_id: int) -> Producto:
        producto = self.productos.obtener(producto_id)
        if producto is None:
            raise NoEncontrado("el producto", producto_id)
        return producto

    def listar(self, usuario: Usuario, sucursal_id: int | None) -> list[StockItem]:
        sucursal = resolver_sucursal(self.sesion, usuario, sucursal_id)
        return [
            StockItem(
                producto_id=producto.id,
                nombre=producto.nombre,
                unidad=producto.unidad,
                precio=producto.precio,
                cantidad=stock.cantidad,
                minimo=stock.minimo,
                bajo_minimo=stock.cantidad < stock.minimo,
            )
            for producto, stock in self.stock.listar_de_sucursal(sucursal.id)
        ]

    def movimientos(
        self,
        usuario: Usuario,
        sucursal_id: int | None,
        producto_id: int | None,
        tipo: str | None,
        desde: date | None,
        hasta: date | None,
        limite: int,
    ) -> list[MovimientoOut]:
        # La dueña puede omitir sucursal_id para ver las dos sucursales.
        sucursal_id = resolver_sucursal_id(usuario, sucursal_id, obligatoria=False)
        movimientos = self.stock.listar_movimientos(sucursal_id, producto_id, tipo, desde, hasta, limite)
        return [movimiento_a_dto(movimiento) for movimiento in movimientos]

    def registrar_merma_o_ajuste(self, usuario: Usuario, datos: MovimientoCrear) -> MovimientoOut:
        """Regla 8: la merma se informa positiva y se guarda negativa; el ajuste lleva signo."""
        sucursal = resolver_sucursal(self.sesion, usuario, datos.sucursal_id)
        producto = self._producto(datos.producto_id)
        cantidad = validar_cantidad(producto, abs(datos.cantidad))
        if datos.tipo == "merma" or datos.cantidad < 0:
            cantidad = -cantidad
        stock = self.libro.bloquear(sucursal, [producto])[producto.id]
        movimiento = self.libro.mover(
            stock, producto, sucursal, datos.tipo, cantidad, usuario.id, motivo=datos.motivo
        )
        if datos.tipo == "merma":
            self.libro.avisos.merma(sucursal, producto, cantidad, usuario, datos.motivo)
        else:
            self.libro.avisos.ajuste(sucursal, producto, cantidad, usuario, datos.motivo)
        self.sesion.flush()
        respuesta = movimiento_a_dto(movimiento)
        self.sesion.commit()
        return respuesta

    def traspasar(self, usuario: Usuario, datos: TraspasoCrear) -> TraspasoOut:
        """Regla 9: un traspaso y dos movimientos en la misma transacción."""
        origen = obtener_sucursal(self.sesion, datos.origen_id)
        destino = obtener_sucursal(self.sesion, datos.destino_id)
        producto = self._producto(datos.producto_id)
        cantidad = validar_cantidad(producto, datos.cantidad)

        # Bloquea las dos filas en orden de sucursal_id; crea la del destino si faltara.
        filas = self.stock.bloquear_en_sucursales(producto.id, [origen.id, destino.id])
        for sucursal in (origen, destino):
            if sucursal.id not in filas:
                filas[sucursal.id] = self.stock.crear(producto.id, sucursal.id)

        traspaso = Traspaso(
            producto_id=producto.id, origen_id=origen.id, destino_id=destino.id, cantidad=cantidad,
            usuario_id=usuario.id, motivo=datos.motivo,
        )
        self.sesion.add(traspaso)
        self.sesion.flush()
        motivo = datos.motivo or f"Traspaso {traspaso.id}"
        self.libro.mover(filas[origen.id], producto, origen, "traspaso_salida", -cantidad, usuario.id,
                         motivo=motivo, traspaso_id=traspaso.id)
        self.libro.mover(filas[destino.id], producto, destino, "traspaso_entrada", cantidad, usuario.id,
                         motivo=motivo, traspaso_id=traspaso.id)
        self.sesion.flush()
        respuesta = TraspasoOut(
            id=traspaso.id, fecha=traspaso.fecha, producto_id=producto.id, producto=producto.nombre,
            unidad=producto.unidad, origen_id=origen.id, destino_id=destino.id, cantidad=cantidad,
            usuario=usuario.nombre, motivo=traspaso.motivo,
        )
        self.sesion.commit()
        return respuesta
