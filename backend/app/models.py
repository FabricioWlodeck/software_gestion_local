"""
Modelos ORM: las tablas de docs/contrato.md, escritas como clases de Python.

Las fechas usan server_default=CURRENT_TIMESTAMP: las pone MariaDB con la hora local del
contenedor (TZ=America/Argentina/Buenos_Aires). Las restricciones CHECK repiten en la base
las reglas que también validan los services: son la última defensa si algo se escapa.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

DINERO = Numeric(12, 2)
CANTIDAD = Numeric(10, 3)
VERDADERO = text("1")


class Sucursal(Base):
    __tablename__ = "sucursal"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)
    activa: Mapped[bool] = mapped_column(default=True, server_default=VERDADERO)


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        CheckConstraint("rol IN ('duenio', 'empleado')", name="rol"),
        # El empleado siempre pertenece a una sucursal; la dueña puede no tener ninguna.
        CheckConstraint("rol = 'duenio' OR sucursal_id IS NOT NULL", name="sucursal_empleado"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_usuario: Mapped[str] = mapped_column(String(40), unique=True)  # el que se usa para entrar
    nombre: Mapped[str] = mapped_column(String(80))
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(10))
    sucursal_id: Mapped[int | None] = mapped_column(ForeignKey("sucursal.id"))
    activo: Mapped[bool] = mapped_column(default=True, server_default=VERDADERO)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    creado_en: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    sucursal: Mapped[Sucursal | None] = relationship()


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint("unidad IN ('kg', 'unidad')", name="unidad"),
        CheckConstraint("modo_precio IN ('manual', 'margen')", name="modo_precio"),
        CheckConstraint("precio > 0", name="precio"),
        CheckConstraint("modo_precio = 'manual' OR margen IS NOT NULL", name="margen"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    unidad: Mapped[str] = mapped_column(String(10))
    modo_precio: Mapped[str] = mapped_column(String(10), default="manual", server_default="manual")
    margen: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))  # porcentaje: 35 = 35 %
    costo_ultimo: Mapped[Decimal | None] = mapped_column(DINERO)
    precio: Mapped[Decimal] = mapped_column(DINERO)
    activo: Mapped[bool] = mapped_column(default=True, server_default=VERDADERO)
    creado_en: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    stocks: Mapped[list["Stock"]] = relationship(back_populates="producto", order_by="Stock.sucursal_id")


class Stock(Base):
    """Saldo actual de un producto en una sucursal. Cada cambio deja un MovimientoStock."""

    __tablename__ = "stock"
    __table_args__ = (
        CheckConstraint("cantidad >= 0", name="cantidad"),
        CheckConstraint("minimo >= 0", name="minimo"),
    )

    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), primary_key=True)
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD, default=Decimal("0"), server_default="0")
    minimo: Mapped[Decimal] = mapped_column(CANTIDAD, default=Decimal("0"), server_default="0")

    producto: Mapped[Producto] = relationship(back_populates="stocks")
    sucursal: Mapped[Sucursal] = relationship()


class Traspaso(Base):
    __tablename__ = "traspaso"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="cantidad"),
        CheckConstraint("origen_id <> destino_id", name="sucursales_distintas"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"))
    origen_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"))
    destino_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"))
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    motivo: Mapped[str | None] = mapped_column(String(200))
    fecha: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    producto: Mapped[Producto] = relationship()
    usuario: Mapped[Usuario] = relationship()


class Caja(Base):
    __tablename__ = "caja"
    __table_args__ = (
        CheckConstraint("estado IN ('abierta', 'cerrada')", name="estado"),
        CheckConstraint("fondo_inicial >= 0", name="fondo_inicial"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"))
    estado: Mapped[str] = mapped_column(String(10))
    abierta_por: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    abierta_en: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    fondo_inicial: Mapped[Decimal] = mapped_column(DINERO)
    cerrada_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    cerrada_en: Mapped[datetime | None]
    efectivo_esperado: Mapped[Decimal | None] = mapped_column(DINERO)
    efectivo_contado: Mapped[Decimal | None] = mapped_column(DINERO)
    diferencia: Mapped[Decimal | None] = mapped_column(DINERO)  # contado − esperado
    observacion: Mapped[str | None] = mapped_column(String(200))

    sucursal: Mapped[Sucursal] = relationship()
    usuario_apertura: Mapped[Usuario] = relationship(foreign_keys=[abierta_por])
    usuario_cierre: Mapped[Usuario | None] = relationship(foreign_keys=[cerrada_por])


class Venta(Base):
    __tablename__ = "venta"
    __table_args__ = (
        CheckConstraint("medio_pago IN ('efectivo', 'transferencia')", name="medio_pago"),
        CheckConstraint("estado IN ('valida', 'observada', 'anulada')", name="estado"),
        Index(None, "sucursal_id", "fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"))
    caja_id: Mapped[int] = mapped_column(ForeignKey("caja.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    fecha: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    medio_pago: Mapped[str] = mapped_column(String(15))
    total: Mapped[Decimal] = mapped_column(DINERO)
    estado: Mapped[str] = mapped_column(String(10), default="valida", server_default="valida")
    motivo_observacion: Mapped[str | None] = mapped_column(String(200))
    observada_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    observada_en: Mapped[datetime | None]
    motivo_resolucion: Mapped[str | None] = mapped_column(String(200))
    resuelta_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    resuelta_en: Mapped[datetime | None]

    sucursal: Mapped[Sucursal] = relationship()
    usuario: Mapped[Usuario] = relationship(foreign_keys=[usuario_id])
    usuario_observacion: Mapped[Usuario | None] = relationship(foreign_keys=[observada_por])
    usuario_resolucion: Mapped[Usuario | None] = relationship(foreign_keys=[resuelta_por])
    detalles: Mapped[list["VentaDetalle"]] = relationship(
        back_populates="venta", cascade="all, delete-orphan", order_by="VentaDetalle.producto_id"
    )


class VentaDetalle(Base):
    __tablename__ = "venta_detalle"
    __table_args__ = (CheckConstraint("cantidad > 0", name="cantidad"),)

    venta_id: Mapped[int] = mapped_column(ForeignKey("venta.id"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD)
    precio_unitario: Mapped[Decimal] = mapped_column(DINERO)  # copia histórica del precio
    subtotal: Mapped[Decimal] = mapped_column(DINERO)

    venta: Mapped[Venta] = relationship(back_populates="detalles")
    producto: Mapped[Producto] = relationship()


class Proveedor(Base):
    __tablename__ = "proveedor"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    telefono: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(120))
    notas: Mapped[str | None] = mapped_column(String(200))
    activo: Mapped[bool] = mapped_column(default=True, server_default=VERDADERO)


class Compra(Base):
    __tablename__ = "compra"

    id: Mapped[int] = mapped_column(primary_key=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedor.id"))
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    fecha: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    comprobante: Mapped[str | None] = mapped_column(String(40))
    total: Mapped[Decimal] = mapped_column(DINERO)

    proveedor: Mapped[Proveedor] = relationship()
    usuario: Mapped[Usuario] = relationship()
    detalles: Mapped[list["CompraDetalle"]] = relationship(
        back_populates="compra", cascade="all, delete-orphan", order_by="CompraDetalle.producto_id"
    )


class CompraDetalle(Base):
    __tablename__ = "compra_detalle"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="cantidad"),
        CheckConstraint("costo_unitario >= 0", name="costo_unitario"),
    )

    compra_id: Mapped[int] = mapped_column(ForeignKey("compra.id"), primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD)
    costo_unitario: Mapped[Decimal] = mapped_column(DINERO)
    subtotal: Mapped[Decimal] = mapped_column(DINERO)

    compra: Mapped[Compra] = relationship(back_populates="detalles")
    producto: Mapped[Producto] = relationship()


class MovimientoStock(Base):
    """Libro de movimientos: cada cambio de stock es una fila nueva, con signo y saldo."""

    __tablename__ = "movimiento_stock"
    __table_args__ = (
        # El signo depende del tipo (y de paso limita los tipos posibles).
        CheckConstraint(
            "(tipo IN ('compra', 'traspaso_entrada', 'anulacion') AND cantidad > 0)"
            " OR (tipo IN ('venta', 'merma', 'traspaso_salida') AND cantidad < 0)"
            " OR (tipo = 'ajuste' AND cantidad <> 0)",
            name="signo",
        ),
        CheckConstraint("tipo NOT IN ('merma', 'ajuste', 'anulacion') OR motivo IS NOT NULL", name="motivo"),
        Index(None, "producto_id", "sucursal_id", "fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"))
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"))
    tipo: Mapped[str] = mapped_column(String(20))
    cantidad: Mapped[Decimal] = mapped_column(CANTIDAD)  # positiva entra, negativa sale
    saldo_resultante: Mapped[Decimal] = mapped_column(CANTIDAD)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    motivo: Mapped[str | None] = mapped_column(String(200))
    venta_id: Mapped[int | None] = mapped_column(ForeignKey("venta.id"))
    compra_id: Mapped[int | None] = mapped_column(ForeignKey("compra.id"))
    traspaso_id: Mapped[int | None] = mapped_column(ForeignKey("traspaso.id"))
    fecha: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    producto: Mapped[Producto] = relationship()
    usuario: Mapped[Usuario] = relationship()


class Notificacion(Base):
    """Tabla de salida (outbox): el bot de Telegram la lee y envía cada mensaje."""

    __tablename__ = "notificacion"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('stock_bajo', 'venta_observada', 'merma', 'ajuste', 'diferencia_caja')", name="tipo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30))
    sucursal_id: Mapped[int | None] = mapped_column(ForeignKey("sucursal.id"))
    mensaje: Mapped[str] = mapped_column(String(500))  # texto listo para enviar por Telegram
    creada_en: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
