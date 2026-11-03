"""
Carga los datos iniciales (usuarios y productos) si la base está vacía.

Ejecutar desde la carpeta de la etapa, después de `alembic upgrade head`:
    python -m app.semilla
Se puede ejecutar varias veces: si ya hay usuarios, no hace nada.
"""

from decimal import Decimal

from sqlalchemy import select

from app.database import SesionLocal
from app.models import Producto, Usuario

USUARIOS = [
    Usuario(nombre="Ana", telefono="555-0101", rol="duenio"),
    Usuario(nombre="Bruno", telefono="555-0102", rol="empleado"),
    Usuario(nombre="Carla", telefono="555-0103", rol="empleado"),
]

PRODUCTOS = [
    Producto(nombre="Queso cremoso", unidad="kg", precio=Decimal("12500.00"), stock=Decimal("2.100")),
    Producto(nombre="Leche entera 1 L", unidad="unidad", precio=Decimal("1450.00"), stock=Decimal("24")),
    Producto(nombre="Salame milán", unidad="kg", precio=Decimal("18900.00"), stock=Decimal("1.500")),
    Producto(nombre="Yogur bebible 1 L", unidad="unidad", precio=Decimal("2300.00"), stock=Decimal("6")),
    Producto(nombre="Queso rallado 150 g", unidad="unidad", precio=Decimal("3100.00"), stock=Decimal("0")),
]


def cargar() -> None:
    with SesionLocal() as sesion:
        if sesion.scalar(select(Usuario).limit(1)) is not None:
            print("La base ya tiene datos: no se cargó nada.")
            return
        sesion.add_all(USUARIOS + PRODUCTOS)
        sesion.commit()
        print(f"Se cargaron {len(USUARIOS)} usuarios y {len(PRODUCTOS)} productos.")


if __name__ == "__main__":
    cargar()
