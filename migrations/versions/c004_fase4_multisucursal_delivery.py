"""Fase 4: Multi-sucursal, delivery, canal en orden

Revision ID: c004_fase4
Revises: c003_fase3
Create Date: 2026-02-15
"""
from alembic import op
import sqlalchemy as sa

revision = 'c004_fase4'
down_revision = 'c003_fase3'
branch_labels = None
depends_on = None


def upgrade():
    # --- Sucursales ---
    op.create_table(
        'sucursales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(100), nullable=False, unique=True),
        sa.Column('direccion', sa.String(300)),
        sa.Column('telefono', sa.String(20)),
        sa.Column('activa', sa.Boolean(), server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- FK sucursal en modelos existentes ---
    op.add_column('usuario', sa.Column('sucursal_id', sa.Integer(),
                  sa.ForeignKey('sucursales.id'), nullable=True))
    op.add_column('mesa', sa.Column('sucursal_id', sa.Integer(),
                  sa.ForeignKey('sucursales.id'), nullable=True))
    op.add_column('orden', sa.Column('sucursal_id', sa.Integer(),
                  sa.ForeignKey('sucursales.id'), nullable=True))
    op.add_column('orden', sa.Column('canal', sa.String(30), server_default='local'))

    # --- Delivery Órdenes ---
    op.create_table(
        'delivery_ordenes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('plataforma', sa.String(30), nullable=False),
        sa.Column('external_id', sa.String(100), nullable=False),
        sa.Column('orden_id', sa.Integer(), sa.ForeignKey('orden.id')),
        sa.Column('estado_plataforma', sa.String(50)),
        sa.Column('payload_raw', sa.Text()),
        sa.Column('cliente_nombre', sa.String(150)),
        sa.Column('cliente_telefono', sa.String(20)),
        sa.Column('direccion_entrega', sa.Text()),
        sa.Column('total_plataforma', sa.Numeric(10, 2)),
        sa.Column('comision', sa.Numeric(10, 2)),
        sa.Column('fecha_recibido', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('fecha_aceptado', sa.DateTime()),
        sa.Column('fecha_listo', sa.DateTime()),
        sa.UniqueConstraint('plataforma', 'external_id', name='uq_delivery_plat_ext'),
    )


def downgrade():
    op.drop_table('delivery_ordenes')
    op.drop_column('orden', 'canal')
    op.drop_column('orden', 'sucursal_id')
    op.drop_column('mesa', 'sucursal_id')
    op.drop_column('usuario', 'sucursal_id')
    op.drop_table('sucursales')
