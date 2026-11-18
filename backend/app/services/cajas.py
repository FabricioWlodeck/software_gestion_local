"""
Caja (regla 7). Una sola caja abierta por sucursal.
Esperado = fondo_inicial + ventas en efectivo no anuladas de la caja. Diferencia = contado − esperado.
"""

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.errores import Conflicto, NoEncontrado
from app.formato import redondear_dinero
from app.models import Caja, Usuario
from app.repositories.cajas import RepositorioCajas
from app.repositories.sucursales import RepositorioSucursales
from app.schemas.caja import CajaAbrir, CajaActual, CajaCerrar, CajaOut
from app.services.avisos import Avisos
from app.services.permisos import resolver_sucursal, verificar_sucursal


def caja_a_dto(caja: Caja) -> CajaOut:
    return CajaOut(
        id=caja.id,
        sucursal_id=caja.sucursal_id,
        estado=caja.estado,
        abierta_por=caja.usuario_apertura.nombre,
        abierta_en=caja.abierta_en,
        fondo_inicial=caja.fondo_inicial,
        cerrada_por=caja.usuario_cierre.nombre if caja.usuario_cierre else None,
        cerrada_en=caja.cerrada_en,
        efectivo_esperado=caja.efectivo_esperado,
        efectivo_contado=caja.efectivo_contado,
        diferencia=caja.diferencia,
        observacion=caja.observacion,
    )


class ServicioCajas:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.cajas = RepositorioCajas(sesion)
        self.sucursales = RepositorioSucursales(sesion)
        self.avisos = Avisos(sesion)

    def actual(self, usuario: Usuario, sucursal_id: int | None) -> CajaActual | None:
        sucursal = resolver_sucursal(self.sesion, usuario, sucursal_id)
        caja = self.cajas.abierta(sucursal.id)
        if caja is None:
            return None
        totales = self.cajas.totales(caja.id)
        return CajaActual(
            **caja_a_dto(caja).model_dump(),
            ventas_efectivo=redondear_dinero(totales.efectivo),
            ventas_transferencia=redondear_dinero(totales.transferencia),
            cantidad_ventas=totales.cantidad,
            efectivo_esperado_actual=redondear_dinero(caja.fondo_inicial + totales.efectivo),
        )

    def abrir(self, usuario: Usuario, datos: CajaAbrir) -> CajaOut:
        sucursal = resolver_sucursal(self.sesion, usuario, datos.sucursal_id)
        # Bloquear la sucursal evita que dos personas abran la caja al mismo tiempo.
        self.sucursales.obtener_para_actualizar(sucursal.id)
        if self.cajas.abierta(sucursal.id, bloqueo="exclusivo") is not None:
            raise Conflicto(f"Ya hay una caja abierta en {sucursal.nombre}")
        caja = self.cajas.agregar(
            Caja(sucursal_id=sucursal.id, estado="abierta", abierta_por=usuario.id, fondo_inicial=datos.fondo_inicial)
        )
        respuesta = caja_a_dto(caja)
        self.sesion.commit()
        return respuesta

    def cerrar(self, usuario: Usuario, caja_id: int, datos: CajaCerrar) -> CajaOut:
        # Bloqueo exclusivo: espera a que terminen las ventas en curso de esta caja.
        caja = self.cajas.obtener(caja_id, para_actualizar=True)
        if caja is None:
            raise NoEncontrado("la caja", caja_id)
        verificar_sucursal(usuario, caja.sucursal_id)
        if caja.estado != "abierta":
            raise Conflicto("La caja ya está cerrada")
        totales = self.cajas.totales(caja.id, bloquear=True)
        esperado = redondear_dinero(caja.fondo_inicial + totales.efectivo)
        diferencia = redondear_dinero(datos.efectivo_contado - esperado)
        caja.estado = "cerrada"
        caja.cerrada_por = usuario.id
        caja.cerrada_en = func.current_timestamp()  # la hora de la base, como las demás fechas
        caja.efectivo_esperado = esperado
        caja.efectivo_contado = datos.efectivo_contado
        caja.diferencia = diferencia
        caja.observacion = datos.observacion
        if diferencia != 0:
            self.avisos.diferencia_caja(caja.sucursal, diferencia, esperado, datos.efectivo_contado)
        self.sesion.flush()
        self.sesion.refresh(caja)  # trae cerrada_en y los usuarios
        respuesta = caja_a_dto(caja)
        self.sesion.commit()
        return respuesta

    def listar(self, sucursal_id: int | None, desde: date | None, hasta: date | None) -> list[CajaOut]:
        return [caja_a_dto(caja) for caja in self.cajas.listar(sucursal_id, desde, hasta)]
