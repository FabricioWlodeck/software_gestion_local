"""
Avisos para la dueña (tabla de salida o outbox, decisión 0004).

Cada método inserta una fila en notificacion dentro de la transacción en curso: si la
operación se descarta, el aviso también. El bot de Telegram lee la tabla y envía el
mensaje tal cual, así que el texto ya va armado, con coma decimal (regla 13).
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.formato import con_punto_final, formatear_cantidad, formatear_dinero
from app.models import Notificacion, Producto, Sucursal, Usuario

LARGO_MAXIMO = 500  # notificacion.mensaje es VARCHAR(500)


class Avisos:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def _agregar(self, tipo: str, sucursal_id: int | None, mensaje: str) -> None:
        if len(mensaje) > LARGO_MAXIMO:
            mensaje = mensaje[: LARGO_MAXIMO - 1] + "…"
        self.sesion.add(Notificacion(tipo=tipo, sucursal_id=sucursal_id, mensaje=mensaje))

    def stock_bajo(self, sucursal: Sucursal, producto: Producto, saldo: Decimal, minimo: Decimal) -> None:
        self._agregar(
            "stock_bajo",
            sucursal.id,
            f"⚠️ Stock bajo en {sucursal.nombre}: {producto.nombre} quedó en "
            f"{formatear_cantidad(saldo, producto.unidad)} (mínimo {formatear_cantidad(minimo, producto.unidad)}).",
        )

    def venta_observada(self, sucursal: Sucursal, venta_id: int, usuario: Usuario, motivo: str) -> None:
        self._agregar(
            "venta_observada",
            sucursal.id,
            f"👀 Venta {venta_id} observada en {sucursal.nombre} por {usuario.nombre}: {con_punto_final(motivo)}",
        )

    def merma(self, sucursal: Sucursal, producto: Producto, cantidad: Decimal, usuario: Usuario, motivo: str) -> None:
        self._agregar(
            "merma",
            sucursal.id,
            f"🗑️ Merma en {sucursal.nombre}: {producto.nombre} {formatear_cantidad(cantidad, producto.unidad)} "
            f"({usuario.nombre}): {con_punto_final(motivo)}",
        )

    def ajuste(self, sucursal: Sucursal, producto: Producto, cantidad: Decimal, usuario: Usuario, motivo: str) -> None:
        self._agregar(
            "ajuste",
            sucursal.id,
            f"🔧 Ajuste en {sucursal.nombre}: {producto.nombre} "
            f"{formatear_cantidad(cantidad, producto.unidad, con_signo=True)} "
            f"({usuario.nombre}): {con_punto_final(motivo)}",
        )

    def diferencia_caja(self, sucursal: Sucursal, diferencia: Decimal, esperado: Decimal, contado: Decimal) -> None:
        self._agregar(
            "diferencia_caja",
            sucursal.id,
            f"💵 Caja de {sucursal.nombre} cerrada con diferencia de {formatear_dinero(diferencia, con_signo=True)} "
            f"(esperado {formatear_dinero(esperado)}, contado {formatear_dinero(contado)}).",
        )
