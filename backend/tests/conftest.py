"""
Pruebas de punta a punta: TestClient → routers → services → MariaDB (base punto_lacteo_test).

- Al empezar, se recrea el esquema de la base de pruebas con Base.metadata.
- Antes de cada prueba se vacían las tablas y se cargan unos datos mínimos conocidos.
  Así cada prueba es independiente, aunque los services hagan commit de verdad.
- Los tokens se fabrican con crear_token (rápido); el inicio de sesión real se prueba aparte.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app import models
from app.config import TEST_DATABASE_URL
from app.database import Base, obtener_sesion
from app.main import app
from app.seguridad import crear_token, hashear

assert "test" in (make_url(TEST_DATABASE_URL).database or ""), "Las pruebas solo corren contra una base *_test"

motor = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
SesionDePrueba = sessionmaker(bind=motor, expire_on_commit=False)

CONTRASENA = "secreto123"


def _sesion_de_prueba() -> Iterator[Session]:
    with SesionDePrueba() as sesion:
        yield sesion


app.dependency_overrides[obtener_sesion] = _sesion_de_prueba


@dataclass
class Datos:
    s1: int
    s2: int
    duenia: int
    bruno: int  # empleado de la Sucursal 1
    carla: int  # empleada de la Sucursal 2
    queso: int  # kg, modo margen 35 % sobre 9259.26 → 12500.00
    leche: int  # unidad, precio manual 1450.00
    proveedor: int


@pytest.fixture(scope="session")
def hash_contrasena() -> str:
    return hashear(CONTRASENA)  # Argon2 es lento a propósito: se calcula una sola vez


@pytest.fixture(scope="session", autouse=True)
def esquema() -> Iterator[None]:
    Base.metadata.drop_all(motor)
    Base.metadata.create_all(motor)
    yield
    motor.dispose()


@pytest.fixture(autouse=True)
def datos(hash_contrasena: str) -> Datos:
    with motor.begin() as conexion:
        conexion.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for tabla in reversed(Base.metadata.sorted_tables):
            conexion.execute(tabla.delete())
        conexion.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    with SesionDePrueba() as sesion:
        s1, s2 = models.Sucursal(nombre="Sucursal 1"), models.Sucursal(nombre="Sucursal 2")
        sesion.add_all([s1, s2])
        sesion.flush()
        duenia = models.Usuario(nombre_usuario="ana", nombre="Ana", rol="duenio", password_hash=hash_contrasena)
        bruno = models.Usuario(nombre_usuario="bruno", nombre="Bruno", rol="empleado", sucursal_id=s1.id,
                               password_hash=hash_contrasena)
        carla = models.Usuario(nombre_usuario="carla", nombre="Carla", rol="empleado", sucursal_id=s2.id,
                               password_hash=hash_contrasena)
        queso = models.Producto(nombre="Queso cremoso", unidad="kg", modo_precio="margen", margen=Decimal("35"),
                                costo_ultimo=Decimal("9259.26"), precio=Decimal("12500.00"))
        leche = models.Producto(nombre="Leche entera 1 L", unidad="unidad", precio=Decimal("1450.00"))
        proveedor = models.Proveedor(nombre="Lácteos del Sur")
        sesion.add_all([duenia, bruno, carla, queso, leche, proveedor])
        sesion.flush()
        sesion.add_all([
            models.Stock(producto_id=queso.id, sucursal_id=s1.id, cantidad=Decimal("5.000"), minimo=Decimal("2.000")),
            models.Stock(producto_id=queso.id, sucursal_id=s2.id, cantidad=Decimal("3.000"), minimo=Decimal("1.000")),
            models.Stock(producto_id=leche.id, sucursal_id=s1.id, cantidad=Decimal("10"), minimo=Decimal("3")),
            models.Stock(producto_id=leche.id, sucursal_id=s2.id, cantidad=Decimal("5"), minimo=Decimal("2")),
        ])
        sesion.commit()
        return Datos(s1.id, s2.id, duenia.id, bruno.id, carla.id, queso.id, leche.id, proveedor.id)


@pytest.fixture
def cliente() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sesion() -> Iterator[Session]:
    """Para mirar la base directamente desde las pruebas."""
    with SesionDePrueba() as sesion:
        yield sesion


def _encabezado(usuario_id: int, rol: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token(usuario_id, rol)}"}


@pytest.fixture
def h_duenia(datos: Datos) -> dict[str, str]:
    return _encabezado(datos.duenia, "duenio")


@pytest.fixture
def h_bruno(datos: Datos) -> dict[str, str]:
    return _encabezado(datos.bruno, "empleado")


@pytest.fixture
def h_carla(datos: Datos) -> dict[str, str]:
    return _encabezado(datos.carla, "empleado")
