"""
Ventas (reglas 3, 4 y 5).

Todo lo que pasa entre la primera consulta y el commit() es una sola transacción: si algo
falla antes del commit, la sesión se cierra sin confirmar y MariaDB descarta los cambios.
No puede quedar una venta guardada sin su descuento de stock, ni al revés.
"""

from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.errores import Conflicto, NoEncontrado
from app.formato import redondear_dinero
from app.models import Producto, Usuario, Venta, VentaDetalle
from app.repositories.cajas import RepositorioCajas
from app.repositories.productos import RepositorioProductos
from app.repositories.ventas import RepositorioVentas
from app.schemas.venta import ItemVentaOut, VentaCrear, VentaOut
from app.services.libro import LibroDeStock, validar_cantidad
from app.services.permisos import es_duenio, resolver_sucursal, resolver_sucursal_id, verificar_sucursal


def venta_a_dto(venta: Venta) -> VentaOut:
    return VentaOut(
        id=venta.id,
        fecha=venta.fecha,
        sucursal_id=venta.sucursal_id,
        caja_id=venta.caja_id,
        usuario_id=venta.usuario_id,
        usuario=venta.usuario.nombre,
        medio_pago=venta.medio_pago,
        total=venta.total,
        estado=venta.estado,
        motivo_observacion=venta.motivo_observacion,
        observada_por=venta.usuario_observacion.nombre if venta.usuario_observacion else None,
        observada_en=venta.observada_en,
        motivo_resolucion=venta.motivo_resolucion,
        resuelta_por=venta.usuario_resolucion.nombre if venta.usuario_resolucion else None,
        resuelta_en=venta.resuelta_en,
        items=[
            ItemVentaOut(
                producto_id=detalle.producto_id,
                producto=detalle.producto.nombre,
                unidad=detalle.producto.unidad,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal,
            )
            for detalle in venta.detalles
        ],
    )


class ServicioVentas:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.ventas = RepositorioVentas(sesion)
        self.cajas = RepositorioCajas(sesion)
        self.productos = RepositorioProductos(sesion)
        self.libro = LibroDeStock(sesion)

    def _obtener(self, usuario: Usuario, venta_id: int, para_actualizar: bool = False) -> Venta:
        venta = self.ventas.obtener(venta_id, para_actualizar)
        if venta is None:
            raise NoEncontrado("la venta", venta_id)
        verificar_sucursal(usuario, venta.sucursal_id)
        return venta

    def _respuesta(self, venta: Venta) -> VentaOut:
        self.sesion.flush()
        self.sesion.refresh(venta)  # trae las fechas que pone la base
        return venta_a_dto(venta)

    def registrar(self, usuario: Usuario, datos: VentaCrear) -> VentaOut:
        sucursal = resolver_sucursal(self.sesion, usuario, datos.sucursal_id)

        # Bloqueo compartido de la caja: el cierre espera a que esta venta termine.
        caja = self.cajas.abierta(sucursal.id, bloqueo="compartido")
        if caja is None:
            raise Conflicto("La caja de la sucursal está cerrada")

        # Si un producto aparece en varias líneas, se suman.
        pedidos: dict[int, Decimal] = defaultdict(Decimal)
        for item in datos.items:
            pedidos[item.producto_id] += item.cantidad

        productos = self.productos.obtener_varios(list(pedidos))
        lineas: list[tuple[Producto, Decimal]] = []
        for producto_id in sorted(pedidos):
            producto = productos.get(producto_id)
            if producto is None:
                raise NoEncontrado("el producto", producto_id)
            if not producto.activo:
                raise Conflicto(f"{producto.nombre} está inactivo y no se puede vender")
            lineas.append((producto, validar_cantidad(producto, pedidos[producto_id])))

        # Bloquea las filas de stock en orden de producto_id (regla 1).
        stocks = self.libro.bloquear(sucursal, [producto for producto, _ in lineas])

        venta = Venta(
            sucursal_id=sucursal.id, caja_id=caja.id, usuario_id=usuario.id, medio_pago=datos.medio_pago,
            total=Decimal("0"),
        )
        for producto, cantidad in lineas:
            venta.detalles.append(
                VentaDetalle(
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,  # copia histórica del precio
                    subtotal=redondear_dinero(cantidad * producto.precio),
                )
            )
        venta.total = redondear_dinero(sum((detalle.subtotal for detalle in venta.detalles), Decimal("0")))
        self.ventas.agregar(venta)

        for producto, cantidad in lineas:
            self.libro.mover(stocks[producto.id], producto, sucursal, "venta", -cantidad, usuario.id,
                             venta_id=venta.id)

        respuesta = self._respuesta(venta)
        self.sesion.commit()  # recién acá se guardan los cambios y se liberan los bloqueos
        return respuesta

    def listar(
        self,
        usuario: Usuario,
        sucursal_id: int | None,
        desde: date | None,
        hasta: date | None,
        estado: str | None,
        limite: int,
    ) -> list[VentaOut]:
        # El empleado solo ve las de hoy de su sucursal; la dueña puede omitir sucursal_id.
        sucursal_id = resolver_sucursal_id(usuario, sucursal_id, obligatoria=False)
        ventas = self.ventas.listar(sucursal_id, desde, hasta, estado, limite, solo_hoy=not es_duenio(usuario))
        return [venta_a_dto(venta) for venta in ventas]

    def obtener(self, usuario: Usuario, venta_id: int) -> VentaOut:
        return venta_a_dto(self._obtener(usuario, venta_id))

    def observar(self, usuario: Usuario, venta_id: int, motivo: str) -> VentaOut:
        """Regla 4: valida → observada, con aviso. No devuelve stock."""
        venta = self._obtener(usuario, venta_id, para_actualizar=True)
        if venta.estado != "valida":
            raise Conflicto("Solo se puede observar una venta válida")
        venta.estado = "observada"
        venta.motivo_observacion = motivo
        venta.observada_por = usuario.id
        venta.observada_en = func.current_timestamp()
        self.libro.avisos.venta_observada(venta.sucursal, venta.id, usuario, motivo)
        respuesta = self._respuesta(venta)
        self.sesion.commit()
        return respuesta

    def confirmar(self, usuario: Usuario, venta_id: int, motivo: str | None) -> VentaOut:
        """Regla 5: observada → valida (solo la dueña)."""
        venta = self._obtener(usuario, venta_id, para_actualizar=True)
        if venta.estado != "observada":
            raise Conflicto("Solo se puede confirmar una venta observada")
        venta.estado = "valida"
        self._resolver(venta, usuario, motivo)
        respuesta = self._respuesta(venta)
        self.sesion.commit()
        return respuesta

    def anular(self, usuario: Usuario, venta_id: int, motivo: str) -> VentaOut:
        """Regla 5: valida u observada → anulada, y devuelve el stock con movimientos 'anulacion'."""
        venta = self._obtener(usuario, venta_id, para_actualizar=True)
        if venta.estado not in ("valida", "observada"):
            raise Conflicto("La venta ya está anulada")
        venta.estado = "anulada"
        self._resolver(venta, usuario, motivo)

        detalles = sorted(venta.detalles, key=lambda detalle: detalle.producto_id)
        stocks = self.libro.bloquear(venta.sucursal, [detalle.producto for detalle in detalles])
        for detalle in detalles:
            self.libro.mover(stocks[detalle.producto_id], detalle.producto, venta.sucursal, "anulacion",
                             detalle.cantidad, usuario.id, motivo=f"Venta {venta.id} anulada: {motivo}",
                             venta_id=venta.id)
        respuesta = self._respuesta(venta)
        self.sesion.commit()
        return respuesta

    def _resolver(self, venta: Venta, usuario: Usuario, motivo: str | None) -> None:
        venta.motivo_resolucion = motivo
        venta.resuelta_por = usuario.id
        venta.resuelta_en = func.current_timestamp()
