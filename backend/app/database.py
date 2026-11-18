"""
Conexión con la base de datos.

- engine: mantiene un pool de conexiones. pool_pre_ping descarta las que MariaDB cerró.
- SesionLocal: fábrica de sesiones (una por petición).
- Base: clase madre de los modelos, con una convención de nombres para las restricciones.

Los services llaman a sesion.commit() de forma explícita antes de devolver: la salida de la
dependencia con yield se ejecuta después de enviar la respuesta, y lo que no se confirmó
se descarta al cerrar la sesión (rollback).
"""

from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL, MOSTRAR_SQL

engine = create_engine(DATABASE_URL, echo=MOSTRAR_SQL, pool_pre_ping=True, pool_recycle=3600)

# expire_on_commit=False: después del commit, los objetos conservan sus valores en memoria.
SesionLocal = sessionmaker(bind=engine, expire_on_commit=False)

CONVENCION_DE_NOMBRES = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCION_DE_NOMBRES)


def obtener_sesion() -> Iterator[Session]:
    """Una sesión por petición. Al salir del with se cierra, y lo que no se confirmó se descarta."""
    with SesionLocal() as sesion:
        yield sesion
