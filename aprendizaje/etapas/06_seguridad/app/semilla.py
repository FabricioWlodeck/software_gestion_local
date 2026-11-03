"""
Carga los datos iniciales y asigna contraseñas de prueba.

Ejecutar desde la carpeta de la etapa, después de `alembic upgrade head`:
    python -m app.semilla

Si la base viene de la etapa 05, los usuarios ya existen sin contraseña: el script
solo les asigna una. Se puede ejecutar varias veces sin duplicar nada.

Las contraseñas son de PRUEBA y están a la vista a propósito. Nunca se usan datos reales.
"""

from decimal import Decimal

from sqlalchemy import select

from app.database import SesionLocal
from app.models import Producto, Usuario
from app.seguridad import hashear

# (nombre, teléfono, rol, contraseña de prueba)
USUARIOS = [
    ("Ana", "555-0101", "duenio", "ana123"),
    ("Bruno", "555-0102", "empleado", "bruno123"),
    ("Carla", "555-0103", "empleado", "carla123"),
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
        for nombre, telefono, rol, contrasena in USUARIOS:
            usuario = sesion.scalars(select(Usuario).where(Usuario.nombre == nombre)).first()
            if usuario is None:
                usuario = Usuario(nombre=nombre, telefono=telefono, rol=rol)
                sesion.add(usuario)
            if usuario.password_hash is None:
                usuario.password_hash = hashear(contrasena)
                print(f"Contraseña de prueba asignada a {nombre} ({rol}).")

        if sesion.scalar(select(Producto).limit(1)) is None:
            sesion.add_all(PRODUCTOS)
            print(f"Se cargaron {len(PRODUCTOS)} productos.")

        sesion.commit()
        print("Datos iniciales listos.")


if __name__ == "__main__":
    cargar()
