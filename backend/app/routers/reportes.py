from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import ServicioReportesDep, solo_duenio
from app.schemas.reporte import Resumen, VentaDiaria

router = APIRouter(prefix="/reportes", tags=["reportes"], dependencies=[Depends(solo_duenio)])


@router.get("/resumen")
def resumen(servicio: ServicioReportesDep, desde: date, hasta: date, sucursal_id: int | None = None) -> Resumen:
    """desde y hasta (AAAA-MM-DD) son inclusivas. Los totales cuentan solo las ventas válidas."""
    return servicio.resumen(desde, hasta, sucursal_id)


@router.get("/ventas-diarias")
def ventas_diarias(
    servicio: ServicioReportesDep, desde: date, hasta: date, sucursal_id: int | None = None
) -> list[VentaDiaria]:
    """Un renglón por día y sucursal con ventas válidas (los días sin ventas no aparecen)."""
    return servicio.ventas_diarias(desde, hasta, sucursal_id)
