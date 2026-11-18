from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.errores import DatosInvalidos
from app.formato import redondear_cantidad, redondear_dinero
from app.repositories.reportes import RepositorioReportes, como_fecha
from app.schemas.reporte import (
    DiferenciaCaja,
    MermaOAjuste,
    Resumen,
    TopProducto,
    TotalesPorMedio,
    TotalSucursal,
    VentaDiaria,
)
from app.services.permisos import obtener_sucursal

CERO = Decimal("0")


class ServicioReportes:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.reportes = RepositorioReportes(sesion)

    def _validar(self, desde: date, hasta: date, sucursal_id: int | None) -> None:
        if desde > hasta:
            raise DatosInvalidos("La fecha desde no puede ser posterior a hasta")
        if sucursal_id is not None:
            obtener_sucursal(self.sesion, sucursal_id)

    def resumen(self, desde: date, hasta: date, sucursal_id: int | None) -> Resumen:
        self._validar(desde, hasta, sucursal_id)

        por_medio = {"efectivo": CERO, "transferencia": CERO}
        por_sucursal: dict[int, list] = {}  # sucursal_id → [total, cantidad]
        for suc_id, medio, total, cantidad in self.reportes.ventas_por_sucursal_y_medio(desde, hasta, sucursal_id):
            por_medio[medio] += total
            acumulado = por_sucursal.setdefault(suc_id, [CERO, 0])
            acumulado[0] += total
            acumulado[1] += cantidad

        estados = self.reportes.contar_por_estado(desde, hasta, sucursal_id)

        return Resumen(
            desde=desde,
            hasta=hasta,
            total=redondear_dinero(sum(por_medio.values(), CERO)),
            cantidad_ventas=estados.get("valida", 0),
            por_medio=TotalesPorMedio(
                efectivo=redondear_dinero(por_medio["efectivo"]),
                transferencia=redondear_dinero(por_medio["transferencia"]),
            ),
            por_sucursal=[
                TotalSucursal(
                    sucursal_id=sucursal.id,
                    nombre=sucursal.nombre,
                    total=redondear_dinero(por_sucursal.get(sucursal.id, [CERO, 0])[0]),
                    cantidad_ventas=por_sucursal.get(sucursal.id, [CERO, 0])[1],
                )
                for sucursal in self.reportes.sucursales(sucursal_id)
            ],
            top_productos=[
                TopProducto(
                    producto_id=producto_id, nombre=nombre, unidad=unidad,
                    cantidad=redondear_cantidad(cantidad), total=redondear_dinero(total),
                )
                for producto_id, nombre, unidad, cantidad, total in self.reportes.top_productos(
                    desde, hasta, sucursal_id
                )
            ],
            ventas_observadas=estados.get("observada", 0),
            ventas_anuladas=estados.get("anulada", 0),
            mermas_y_ajustes=[
                MermaOAjuste(
                    fecha=fecha, sucursal_id=suc_id, producto=producto, unidad=unidad, tipo=tipo,
                    cantidad=cantidad, usuario=usuario, motivo=motivo,
                )
                for fecha, suc_id, producto, unidad, tipo, cantidad, usuario, motivo
                in self.reportes.mermas_y_ajustes(desde, hasta, sucursal_id)
            ],
            diferencias_caja=[
                DiferenciaCaja(caja_id=caja_id, sucursal_id=suc_id, cerrada_en=cerrada_en, diferencia=diferencia)
                for caja_id, suc_id, cerrada_en, diferencia in self.reportes.diferencias_caja(
                    desde, hasta, sucursal_id
                )
            ],
        )

    def ventas_diarias(self, desde: date, hasta: date, sucursal_id: int | None) -> list[VentaDiaria]:
        self._validar(desde, hasta, sucursal_id)
        return [
            VentaDiaria(fecha=como_fecha(dia), sucursal_id=suc_id, total=redondear_dinero(total), cantidad=cantidad)
            for dia, suc_id, total, cantidad in self.reportes.ventas_diarias(desde, hasta, sucursal_id)
        ]
