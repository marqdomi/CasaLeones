"""Fase 3: Inventario, CRM, Reservaciones, CFDI, Mesa avanzada

Revision ID: c003_fase3
Revises: c002_fase2
Create Date: 2026-02-15
"""
from alembic import op
import sqlalchemy as sa

revision = 'c003_fase3'
down_revision = 'c002_fase2'
branch_labels = None
depends_on = None


def upgrade():
    # --- Clientes ---
    op.create_table(
        'clientes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(150), nullable=False),
        sa.Column('telefono', sa.String(20)),
        sa.Column('email', sa.String(120)),
        sa.Column('rfc', sa.String(13)),
        sa.Column('razon_social', sa.String(200)),
        sa.Column('uso_cfdi', sa.String(10)),
        sa.Column('domicilio_fiscal', sa.String(10)),
        sa.Column('notas', sa.Text()),
        sa.Column('fecha_registro', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('visitas', sa.Integer(), server_default='0'),
        sa.Column('total_gastado', sa.Numeric(12, 2), server_default='0'),
    )

    # --- Reservaciones ---
    op.create_table(
        'reservaciones',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mesa_id', sa.Integer(), sa.ForeignKey('mesa.id')),
        sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clientes.id')),
        sa.Column('nombre_contacto', sa.String(150), nullable=False),
        sa.Column('telefono', sa.String(20)),
        sa.Column('fecha_hora', sa.DateTime(), nullable=False),
        sa.Column('num_personas', sa.Integer(), server_default='2'),
        sa.Column('estado', sa.String(20), server_default="'confirmada'"),
        sa.Column('notas', sa.Text()),
        sa.Column('creada_por', sa.Integer(), sa.ForeignKey('usuario.id')),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- Ingredientes ---
    op.create_table(
        'ingredientes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(150), nullable=False, unique=True),
        sa.Column('unidad', sa.String(30), nullable=False),
        sa.Column('stock_actual', sa.Numeric(12, 4), server_default='0'),
        sa.Column('stock_minimo', sa.Numeric(12, 4), server_default='0'),
        sa.Column('costo_unitario', sa.Numeric(10, 2), server_default='0'),
        sa.Column('activo', sa.Boolean(), server_default='true'),
    )

    # --- Receta Detalle ---
    op.create_table(
        'receta_detalle',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('producto_id', sa.Integer(), sa.ForeignKey('producto.id'), nullable=False),
        sa.Column('ingrediente_id', sa.Integer(), sa.ForeignKey('ingredientes.id'), nullable=False),
        sa.Column('cantidad_por_unidad', sa.Numeric(12, 4), nullable=False),
        sa.UniqueConstraint('producto_id', 'ingrediente_id', name='uq_receta_prod_ing'),
    )

    # --- Movimientos de Inventario ---
    op.create_table(
        'movimientos_inventario',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ingrediente_id', sa.Integer(), sa.ForeignKey('ingredientes.id'), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('cantidad', sa.Numeric(12, 4), nullable=False),
        sa.Column('costo', sa.Numeric(10, 2)),
        sa.Column('motivo', sa.String(200)),
        sa.Column('orden_id', sa.Integer(), sa.ForeignKey('orden.id')),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuario.id'), nullable=False),
        sa.Column('fecha', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- Facturas CFDI ---
    op.create_table(
        'facturas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('orden_id', sa.Integer(), sa.ForeignKey('orden.id'), nullable=False),
        sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clientes.id'), nullable=False),
        sa.Column('uuid_cfdi', sa.String(40), unique=True),
        sa.Column('serie', sa.String(10)),
        sa.Column('folio', sa.String(20)),
        sa.Column('rfc_receptor', sa.String(13), nullable=False),
        sa.Column('razon_social', sa.String(200), nullable=False),
        sa.Column('uso_cfdi', sa.String(10), server_default="'G03'"),
        sa.Column('regimen_fiscal', sa.String(5)),
        sa.Column('domicilio_fiscal', sa.String(10)),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('iva', sa.Numeric(10, 2), nullable=False),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('estado', sa.String(20), server_default="'pendiente'"),
        sa.Column('xml_url', sa.String(500)),
        sa.Column('pdf_url', sa.String(500)),
        sa.Column('pac_response', sa.Text()),
        sa.Column('fecha_timbrado', sa.DateTime()),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- Mesa: campos avanzados ---
    op.add_column('mesa', sa.Column('capacidad', sa.Integer(), server_default='4'))
    op.add_column('mesa', sa.Column('estado', sa.String(20), server_default="'disponible'"))
    op.add_column('mesa', sa.Column('zona', sa.String(50)))
    op.add_column('mesa', sa.Column('pos_x', sa.Integer()))
    op.add_column('mesa', sa.Column('pos_y', sa.Integer()))

    # --- Orden: FK a cliente ---
    op.add_column('orden', sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clientes.id')))


def downgrade():
    op.drop_column('orden', 'cliente_id')
    for col in ['pos_y', 'pos_x', 'zona', 'estado', 'capacidad']:
        op.drop_column('mesa', col)
    op.drop_table('facturas')
    op.drop_table('movimientos_inventario')
    op.drop_table('receta_detalle')
    op.drop_table('ingredientes')
    op.drop_table('reservaciones')
    op.drop_table('clientes')
