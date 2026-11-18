"""
Datos iniciales del MVP (docs/contrato.md, «Datos iniciales»).

Ejecutar después de `alembic upgrade head`:   python -m app.semilla

Solo carga datos si no hay ninguna sucursal, así que se puede ejecutar en cada arranque
del contenedor sin duplicar nada. Las contraseñas salen de variables de entorno (.env).
El stock inicial se carga como movimientos «ajuste» con motivo «Stock inicial», sin
notificaciones (no son avisos para la dueña).
"""

import os
import sys
from decimal import Decimal

from sqlalchemy import select

from app.database import SesionLocal
from app.formato import redondear_dinero
from app.models import MovimientoStock, Producto, Proveedor, Stock, Sucursal, Usuario
from app.seguridad import hashear

SUCURSALES = ["Sucursal 1", "Sucursal 2"]

# (nombre, unidad, modo, margen, costo, precio manual,
#  (stock Sucursal 1, mínimo Sucursal 1), (stock Sucursal 2, mínimo Sucursal 2))
PRODUCTOS = [
    ("Queso cremoso", "kg", "margen", "35", "9259.26", None, ("8.500", "2.000"), ("4.200", "1.500")),
    ("Queso de máquina", "kg", "margen", "40", "8500.00", None, ("6.000", "1.500"), ("3.500", "1.000")),
    ("Queso sardo", "kg", "manual", None, "12000.00", "16800.00", ("3.200", "1.000"), ("2.000", "0.800")),
    ("Queso azul", "kg", "manual", None, "13900.00", "19500.00", ("1.800", "0.500"), ("1.200", "0.500")),
    ("Jamón cocido", "kg", "margen", "40", "10000.00", None, ("5.000", "1.500"), ("3.000", "1.000")),
    ("Salame milán", "kg", "margen", "40", "13500.00", None, ("2.500", "1.000"), ("1.800", "0.700")),
    ("Mortadela", "kg", "manual", None, "5600.00", "7900.00", ("4.000", "1.000"), ("2.500", "1.000")),
    ("Leche entera 1 L", "unidad", "manual", None, "1100.00", "1450.00", ("48", "12"), ("36", "12")),
    ("Yogur bebible 1 L", "unidad", "manual", None, "1700.00", "2300.00", ("24", "6"), ("18", "6")),
    ("Manteca 200 g", "unidad", "margen", "30", "2000.00", None, ("20", "5"), ("15", "5")),
    ("Dulce de leche 400 g", "unidad", "manual", None, "2400.00", "3200.00", ("18", "4"), ("12", "4")),
    ("Crema de leche 200 ml", "unidad", "manual", None, "1400.00", "1900.00", ("15", "4"), ("10", "4")),
]

PROVEEDORES = [
    Proveedor(nombre="Lácteos del Sur", telefono="11 4555-0101", email="ventas@lacteosdelsur.example"),
    Proveedor(nombre="Fiambres La Colonia", telefono="11 4555-0202", notas="Entrega martes y viernes"),
]


def _variable(nombre: str) -> str:
    valor = os.getenv(nombre, "").strip()
    if not valor:
        sys.exit(f"Falta la variable de entorno {nombre} (ver .env.sample).")
    return valor


def cargar() -> None:
    with SesionLocal() as sesion:
        if sesion.scalar(select(Sucursal).limit(1)) is not None:
            print("Semilla: la base ya tiene datos, no se carga nada.")
            return

        duenia_usuario = _variable("DUENIA_USUARIO")
        duenia_nombre = _variable("DUENIA_NOMBRE")
        duenia_contrasena = _variable("DUENIA_CONTRASENA")
        contrasena_empleados = _variable("SEMILLA_CONTRASENA_EMPLEADOS")

        sucursales = [Sucursal(nombre=nombre) for nombre in SUCURSALES]
        sesion.add_all(sucursales)
        sesion.flush()

        duenia = Usuario(
            nombre_usuario=duenia_usuario, nombre=duenia_nombre, rol="duenio", password_hash=hashear(duenia_contrasena)
        )
        hash_empleados = hashear(contrasena_empleados)
        empleados = [
            Usuario(nombre_usuario="bruno", nombre="Bruno", rol="empleado", sucursal_id=sucursales[0].id,
                    password_hash=hash_empleados),
            Usuario(nombre_usuario="carla", nombre="Carla", rol="empleado", sucursal_id=sucursales[1].id,
                    password_hash=hash_empleados),
        ]
        sesion.add_all([duenia, *empleados])
        sesion.flush()

        for nombre, unidad, modo, margen, costo, precio, *stocks in PRODUCTOS:
            costo_ultimo = Decimal(costo)
            if modo == "margen":
                precio_final = redondear_dinero(costo_ultimo * (1 + Decimal(margen) / 100))
            else:
                precio_final = Decimal(precio)
            producto = Producto(
                nombre=nombre, unidad=unidad, modo_precio=modo, margen=Decimal(margen) if margen else None,
                costo_ultimo=costo_ultimo, precio=precio_final,
            )
            sesion.add(producto)
            sesion.flush()
            for sucursal, (cantidad, minimo) in zip(sucursales, stocks):
                cantidad = Decimal(cantidad)
                sesion.add(Stock(producto_id=producto.id, sucursal_id=sucursal.id, cantidad=cantidad,
                                 minimo=Decimal(minimo)))
                sesion.add(MovimientoStock(
                    producto_id=producto.id, sucursal_id=sucursal.id, tipo="ajuste", cantidad=cantidad,
                    saldo_resultante=cantidad, usuario_id=duenia.id, motivo="Stock inicial",
                ))

        sesion.add_all(PROVEEDORES)
        sesion.commit()

        print(
            f"Semilla cargada: {len(sucursales)} sucursales, 3 usuarios "
            f"({duenia_usuario} dueña, bruno en {sucursales[0].nombre}, carla en {sucursales[1].nombre}), "
            f"{len(PRODUCTOS)} productos con stock inicial y {len(PROVEEDORES)} proveedores."
        )


if __name__ == "__main__":
    cargar()
