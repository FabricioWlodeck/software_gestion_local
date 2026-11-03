"""
Modelos ORM: las mismas cuatro tablas de la etapa 04, escritas como clases de Python.

Cada atributo Mapped[...] es una columna. Las relaciones (relationship) no son columnas:
permiten navegar de un objeto a otro, por ejemplo venta.detalles o detalle.producto.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (CheckConstraint("rol IN ('duenio', 'empleado')", name="ck_usuario_rol"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    telefono: Mapped[str | None] = mapped_column(String(30))
    rol: Mapped[str] = mapped_column(String(20))
    # Nueva en la etapa 06 (migración 0002). Nunca se guarda la contraseña, solo su hash.
    # Admite NULL porque los usuarios que ya existían no tienen contraseña: no pueden entrar hasta tenerla.
    password_hash: Mapped[str | None] = mapped_column(String(255))


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint("unidad IN ('kg', 'unidad')", name="ck_producto_unidad"),
        CheckConstraint("precio > 0", name="ck_producto_precio"),
        CheckConstraint("stock >= 0", name="ck_producto_stock"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    unidad: Mapped[str] = mapped_column(String(10))
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=Decimal("0"))


class Venta(Base):
    __tablename__ = "venta"

    id: Mapped[int] = mapped_column(primary_key=True)
    # CURRENT_TIMESTAMP existe en MariaDB, PostgreSQL y SQLite (now() no existe en SQLite).
    fecha: Mapped[datetime] = mapped_column(server_default=func.current_timestamp(), index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    usuario: Mapped[Usuario] = relationship()
    detalles: Mapped[list["VentaDetalle"]] = relationship(back_populates="venta", cascade="all, delete-orphan")

    @property
    def items(self) -> list["VentaDetalle"]:
        """Nombre que usa el schema VentaOut para las líneas (el contrato de la etapa 03)."""
        return self.detalles


class VentaDetalle(Base):
    __tablename__ = "venta_detalle"
    __table_args__ = (CheckConstraint("cantidad > 0", name="ck_detalle_cantidad"),)

    venta_id: Mapped[int] = mapped_column(ForeignKey("venta.id", ondelete="CASCADE"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), primary_key=True)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    venta: Mapped[Venta] = relationship(back_populates="detalles")
    producto: Mapped[Producto] = relationship()

    @property
    def nombre(self) -> str:
        return self.producto.nombre

    @property
    def subtotal(self) -> Decimal:
        return (self.cantidad * self.precio_unitario).quantize(Decimal("0.01"))
