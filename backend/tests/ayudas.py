"""Ayudas para armar escenarios en las pruebas."""

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def abrir_caja(cliente: TestClient, headers: dict, sucursal_id: int | None = None, fondo: str = "10000.00") -> dict:
    cuerpo = {"fondo_inicial": fondo}
    if sucursal_id is not None:
        cuerpo["sucursal_id"] = sucursal_id
    respuesta = cliente.post("/cajas", json=cuerpo, headers=headers)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def vender(cliente: TestClient, headers: dict, items: list[tuple[int, str]], medio: str = "efectivo",
           sucursal_id: int | None = None, esperado: int = 201) -> dict:
    cuerpo = {"medio_pago": medio, "items": [{"producto_id": p, "cantidad": c} for p, c in items]}
    if sucursal_id is not None:
        cuerpo["sucursal_id"] = sucursal_id
    respuesta = cliente.post("/ventas", json=cuerpo, headers=headers)
    assert respuesta.status_code == esperado, respuesta.text
    return respuesta.json()


def _foto_nueva(sesion: Session) -> None:
    """Termina la transacción de la sesión de prueba: con REPEATABLE READ, una transacción
    abierta sigue viendo la «foto» de su primera lectura y no vería lo que hizo la API."""
    sesion.rollback()


def stock_de(sesion: Session, producto_id: int, sucursal_id: int) -> Decimal:
    _foto_nueva(sesion)
    return sesion.get(models.Stock, (producto_id, sucursal_id)).cantidad


def notificaciones(sesion: Session, tipo: str | None = None) -> list[models.Notificacion]:
    _foto_nueva(sesion)
    consulta = select(models.Notificacion).order_by(models.Notificacion.id)
    if tipo is not None:
        consulta = consulta.where(models.Notificacion.tipo == tipo)
    return list(sesion.scalars(consulta))


def movimientos(sesion: Session, **filtros) -> list[models.MovimientoStock]:
    _foto_nueva(sesion)
    consulta = select(models.MovimientoStock).filter_by(**filtros).order_by(models.MovimientoStock.id)
    return list(sesion.scalars(consulta))
