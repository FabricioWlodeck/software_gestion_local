"""
Conexión con la base de datos.

- engine: sabe cómo conectarse y mantiene un pool (grupo) de conexiones abiertas para reutilizarlas.
- SesionLocal: fábrica de sesiones. Una sesión es una conversación con la base durante una
  petición: agrupa las consultas y los cambios hasta que se confirman con commit().
- Base: clase madre de los modelos. Cada subclase representa una tabla.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL, MOSTRAR_SQL

engine = create_engine(DATABASE_URL, echo=MOSTRAR_SQL, pool_pre_ping=True)

# expire_on_commit=False: después del commit, los objetos conservan sus valores en memoria.
SesionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def obtener_sesion() -> Iterator[Session]:
    """Una sesión por petición. Al salir del with se cierra, y lo que no se confirmó se descarta."""
    with SesionLocal() as sesion:
        yield sesion
