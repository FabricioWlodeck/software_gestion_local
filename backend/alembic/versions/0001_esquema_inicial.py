"""esquema inicial

Crea las 13 tablas de docs/contrato.md con sus CHECK, índices y valores por defecto.
Generada con --autogenerate y revisada a mano: los CHECK de signo y motivo de
movimiento_stock, los índices (sucursal_id, fecha) y (producto_id, sucursal_id, fecha)
y los DEFAULT de fechas y booleanos están presentes.

Revision ID: 0001
Revises:
Create Date: 2026-11-15 18:03:24.577583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('producto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=80), nullable=False),
    sa.Column('unidad', sa.String(length=10), nullable=False),
    sa.Column('modo_precio', sa.String(length=10), server_default='manual', nullable=False),
    sa.Column('margen', sa.Numeric(precision=6, scale=2), nullable=True),
    sa.Column('costo_ultimo', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('precio', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('activo', sa.Boolean(), server_default=sa.text('1'), nullable=False),
    sa.Column('creado_en', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint("modo_precio = 'manual' OR margen IS NOT NULL", name=op.f('ck_producto_margen')),
    sa.CheckConstraint("modo_precio IN ('manual', 'margen')", name=op.f('ck_producto_modo_precio')),
    sa.CheckConstraint("unidad IN ('kg', 'unidad')", name=op.f('ck_producto_unidad')),
    sa.CheckConstraint('precio > 0', name=op.f('ck_producto_precio')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_producto')),
    sa.UniqueConstraint('nombre', name=op.f('uq_producto_nombre'))
    )
    op.create_table('proveedor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=80), nullable=False),
    sa.Column('telefono', sa.String(length=40), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('notas', sa.String(length=200), nullable=True),
    sa.Column('activo', sa.Boolean(), server_default=sa.text('1'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_proveedor')),
    sa.UniqueConstraint('nombre', name=op.f('uq_proveedor_nombre'))
    )
    op.create_table('sucursal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=60), nullable=False),
    sa.Column('activa', sa.Boolean(), server_default=sa.text('1'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sucursal')),
    sa.UniqueConstraint('nombre', name=op.f('uq_sucursal_nombre'))
    )
    op.create_table('notificacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('sucursal_id', sa.Integer(), nullable=True),
    sa.Column('mensaje', sa.String(length=500), nullable=False),
    sa.Column('creada_en', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint("tipo IN ('stock_bajo', 'venta_observada', 'merma', 'ajuste', 'diferencia_caja')", name=op.f('ck_notificacion_tipo')),
    sa.ForeignKeyConstraint(['sucursal_id'], ['sucursal.id'], name=op.f('fk_notificacion_sucursal_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notificacion'))
    )
    op.create_table('stock',
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('sucursal_id', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Numeric(precision=10, scale=3), server_default='0', nullable=False),
    sa.Column('minimo', sa.Numeric(precision=10, scale=3), server_default='0', nullable=False),
    sa.CheckConstraint('cantidad >= 0', name=op.f('ck_stock_cantidad')),
    sa.CheckConstraint('minimo >= 0', name=op.f('ck_stock_minimo')),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], name=op.f('fk_stock_producto_id')),
    sa.ForeignKeyConstraint(['sucursal_id'], ['sucursal.id'], name=op.f('fk_stock_sucursal_id')),
    sa.PrimaryKeyConstraint('producto_id', 'sucursal_id', name=op.f('pk_stock'))
    )
    op.create_table('usuario',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre_usuario', sa.String(length=40), nullable=False),
    sa.Column('nombre', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('rol', sa.String(length=10), nullable=False),
    sa.Column('sucursal_id', sa.Integer(), nullable=True),
    sa.Column('activo', sa.Boolean(), server_default=sa.text('1'), nullable=False),
    sa.Column('telegram_id', sa.BigInteger(), nullable=True),
    sa.Column('creado_en', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint("rol = 'duenio' OR sucursal_id IS NOT NULL", name=op.f('ck_usuario_sucursal_empleado')),
    sa.CheckConstraint("rol IN ('duenio', 'empleado')", name=op.f('ck_usuario_rol')),
    sa.ForeignKeyConstraint(['sucursal_id'], ['sucursal.id'], name=op.f('fk_usuario_sucursal_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_usuario')),
    sa.UniqueConstraint('nombre_usuario', name=op.f('uq_usuario_nombre_usuario')),
    sa.UniqueConstraint('telegram_id', name=op.f('uq_usuario_telegram_id'))
    )
    op.create_table('caja',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sucursal_id', sa.Integer(), nullable=False),
    sa.Column('estado', sa.String(length=10), nullable=False),
    sa.Column('abierta_por', sa.Integer(), nullable=False),
    sa.Column('abierta_en', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('fondo_inicial', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('cerrada_por', sa.Integer(), nullable=True),
    sa.Column('cerrada_en', sa.DateTime(), nullable=True),
    sa.Column('efectivo_esperado', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('efectivo_contado', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('diferencia', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('observacion', sa.String(length=200), nullable=True),
    sa.CheckConstraint("estado IN ('abierta', 'cerrada')", name=op.f('ck_caja_estado')),
    sa.CheckConstraint('fondo_inicial >= 0', name=op.f('ck_caja_fondo_inicial')),
    sa.ForeignKeyConstraint(['abierta_por'], ['usuario.id'], name=op.f('fk_caja_abierta_por')),
    sa.ForeignKeyConstraint(['cerrada_por'], ['usuario.id'], name=op.f('fk_caja_cerrada_por')),
    sa.ForeignKeyConstraint(['sucursal_id'], ['sucursal.id'], name=op.f('fk_caja_sucursal_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_caja'))
    )
    op.create_table('compra',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('proveedor_id', sa.Integer(), nullable=False),
    sa.Column('sucursal_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('comprobante', sa.String(length=40), nullable=True),
    sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['proveedor_id'], ['proveedor.id'], name=op.f('fk_compra_proveedor_id')),
    sa.ForeignKeyConstraint(['sucursal_id'], ['sucursal.id'], name=op.f('fk_compra_sucursal_id')),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], name=op.f('fk_compra_usuario_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_compra'))
    )
    op.create_table('traspaso',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('origen_id', sa.Integer(), nullable=False),
    sa.Column('destino_id', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('motivo', sa.String(length=200), nullable=True),
    sa.Column('fecha', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint('cantidad > 0', name=op.f('ck_traspaso_cantidad')),
    sa.CheckConstraint('origen_id <> destino_id', name=op.f('ck_traspaso_sucursales_distintas')),
    sa.ForeignKeyConstraint(['destino_id'], ['sucursal.id'], name=op.f('fk_traspaso_destino_id')),
    sa.ForeignKeyConstraint(['origen_id'], ['sucursal.id'], name=op.f('fk_traspaso_origen_id')),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], name=op.f('fk_traspaso_producto_id')),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], name=op.f('fk_traspaso_usuario_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_traspaso'))
    )
    op.create_table('compra_detalle',
    sa.Column('compra_id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('costo_unitario', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.CheckConstraint('cantidad > 0', name=op.f('ck_compra_detalle_cantidad')),
    sa.CheckConstraint('costo_unitario >= 0', name=op.f('ck_compra_detalle_costo_unitario')),
    sa.ForeignKeyConstraint(['compra_id'], ['compra.id'], name=op.f('fk_compra_detalle_compra_id')),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], name=op.f('fk_compra_detalle_producto_id')),
    sa.PrimaryKeyConstraint('compra_id', 'producto_id', name=op.f('pk_compra_detalle'))
    )
    op.create_table('venta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sucursal_id', sa.Integer(), nullable=False),
    sa.Column('caja_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('medio_pago', sa.String(length=15), nullable=False),
    sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('estado', sa.String(length=10), server_default='valida', nullable=False),
    sa.Column('motivo_observacion', sa.String(length=200), nullable=True),
    sa.Column('observada_por', sa.Integer(), nullable=True),
    sa.Column('observada_en', sa.DateTime(), nullable=True),
    sa.Column('motivo_resolucion', sa.String(length=200), nullable=True),
    sa.Column('resuelta_por', sa.Integer(), nullable=True),
    sa.Column('resuelta_en', sa.DateTime(), nullable=True),
    sa.CheckConstraint("estado IN ('valida', 'observada', 'anulada')", name=op.f('ck_venta_estado')),
    sa.CheckConstraint("medio_pago IN ('efectivo', 'transferencia')", name=op.f('ck_venta_medio_pago')),
    sa.ForeignKeyConstraint(['caja_id'], ['caja.id'], name=op.f('fk_venta_caja_id')),
    sa.ForeignKeyConstraint(['observada_por'], ['usuario.id'], name=op.f('fk_venta_observada_por')),
    sa.ForeignKeyConstraint(['resuelta_por'], ['usuario.id'], name=op.f('fk_venta_resuelta_por')),
    sa.ForeignKeyConstraint(['sucursal_id'], ['sucursal.id'], name=op.f('fk_venta_sucursal_id')),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], name=op.f('fk_venta_usuario_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_venta'))
    )
    op.create_index(op.f('ix_venta_sucursal_id_fecha'), 'venta', ['sucursal_id', 'fecha'], unique=False)
    op.create_table('movimiento_stock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('sucursal_id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('cantidad', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('saldo_resultante', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('motivo', sa.String(length=200), nullable=True),
    sa.Column('venta_id', sa.Integer(), nullable=True),
    sa.Column('compra_id', sa.Integer(), nullable=True),
    sa.Column('traspaso_id', sa.Integer(), nullable=True),
    sa.Column('fecha', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint("(tipo IN ('compra', 'traspaso_entrada', 'anulacion') AND cantidad > 0) OR (tipo IN ('venta', 'merma', 'traspaso_salida') AND cantidad < 0) OR (tipo = 'ajuste' AND cantidad <> 0)", name=op.f('ck_movimiento_stock_signo')),
    sa.CheckConstraint("tipo NOT IN ('merma', 'ajuste', 'anulacion') OR motivo IS NOT NULL", name=op.f('ck_movimiento_stock_motivo')),
    sa.ForeignKeyConstraint(['compra_id'], ['compra.id'], name=op.f('fk_movimiento_stock_compra_id')),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], name=op.f('fk_movimiento_stock_producto_id')),
    sa.ForeignKeyConstraint(['sucursal_id'], ['sucursal.id'], name=op.f('fk_movimiento_stock_sucursal_id')),
    sa.ForeignKeyConstraint(['traspaso_id'], ['traspaso.id'], name=op.f('fk_movimiento_stock_traspaso_id')),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], name=op.f('fk_movimiento_stock_usuario_id')),
    sa.ForeignKeyConstraint(['venta_id'], ['venta.id'], name=op.f('fk_movimiento_stock_venta_id')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_movimiento_stock'))
    )
    op.create_index(op.f('ix_movimiento_stock_producto_id_sucursal_id_fecha'), 'movimiento_stock', ['producto_id', 'sucursal_id', 'fecha'], unique=False)
    op.create_table('venta_detalle',
    sa.Column('venta_id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('precio_unitario', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.CheckConstraint('cantidad > 0', name=op.f('ck_venta_detalle_cantidad')),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], name=op.f('fk_venta_detalle_producto_id')),
    sa.ForeignKeyConstraint(['venta_id'], ['venta.id'], name=op.f('fk_venta_detalle_venta_id')),
    sa.PrimaryKeyConstraint('venta_id', 'producto_id', name=op.f('pk_venta_detalle'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('venta_detalle')
    op.drop_index(op.f('ix_movimiento_stock_producto_id_sucursal_id_fecha'), table_name='movimiento_stock')
    op.drop_table('movimiento_stock')
    op.drop_index(op.f('ix_venta_sucursal_id_fecha'), table_name='venta')
    op.drop_table('venta')
    op.drop_table('compra_detalle')
    op.drop_table('traspaso')
    op.drop_table('compra')
    op.drop_table('caja')
    op.drop_table('usuario')
    op.drop_table('stock')
    op.drop_table('notificacion')
    op.drop_table('sucursal')
    op.drop_table('proveedor')
    op.drop_table('producto')
