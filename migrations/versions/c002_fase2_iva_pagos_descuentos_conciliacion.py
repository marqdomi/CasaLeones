"""Fase 2: IVA, multi-pago, descuentos, conciliación de caja

Revision ID: c002_fase2
Revises: c001_precio_unitario
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa

revision = 'c002_fase2'
down_revision = 'c001_precio_unitario'
branch_labels = None
depends_on = None


def upgrade():
    # --- Orden: campos fiscales y descuento ---
    for col in [
        ('subtotal', sa.Numeric(10, 2)),
        ('iva', sa.Numeric(10, 2)),
        ('total', sa.Numeric(10, 2)),
        ('descuento_pct', sa.Numeric(5, 2)),
        ('descuento_monto', sa.Numeric(10, 2)),
        ('descuento_motivo', sa.String(200)),
        ('descuento_autorizado_por', sa.Integer()),
        ('propina', sa.Numeric(10, 2)),
    ]:
        op.add_column('orden', sa.Column(col[0], col[1], nullable=True))

    # FK para descuento_autorizado_por
    op.create_foreign_key(
        'fk_orden_descuento_autorizado_por',
        'orden', 'usuario',
        ['descuento_autorizado_por'], ['id'],
    )

    # Cambiar monto_recibido y cambio a Numeric
    op.alter_column('orden', 'monto_recibido',
                    type_=sa.Numeric(10, 2), existing_type=sa.Float())
    op.alter_column('orden', 'cambio',
                    type_=sa.Numeric(10, 2), existing_type=sa.Float())

    # --- Tabla Pagos ---
    op.create_table(
        'pagos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('orden_id', sa.Integer(), sa.ForeignKey('orden.id'), nullable=False),
        sa.Column('metodo', sa.String(30), nullable=False),
        sa.Column('monto', sa.Numeric(10, 2), nullable=False),
        sa.Column('referencia', sa.String(100), nullable=True),
        sa.Column('fecha', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('registrado_por', sa.Integer(), sa.ForeignKey('usuario.id'), nullable=False),
    )

    # --- CorteCaja: campos de conciliación ---
    for col in [
        ('efectivo_esperado', sa.Numeric(10, 2)),
        ('efectivo_contado', sa.Numeric(10, 2)),
        ('diferencia', sa.Numeric(10, 2)),
        ('tarjeta_total', sa.Numeric(10, 2)),
        ('transferencia_total', sa.Numeric(10, 2)),
        ('notas', sa.Text()),
    ]:
        op.add_column('corte_caja', sa.Column(col[0], col[1], nullable=True))

    # Cambiar Producto.precio de Float a Numeric
    op.alter_column('producto', 'precio',
                    type_=sa.Numeric(10, 2), existing_type=sa.Float())


def downgrade():
    op.alter_column('producto', 'precio',
                    type_=sa.Float(), existing_type=sa.Numeric(10, 2))

    for col in ['notas', 'transferencia_total', 'tarjeta_total',
                'diferencia', 'efectivo_contado', 'efectivo_esperado']:
        op.drop_column('corte_caja', col)

    op.drop_table('pagos')

    op.drop_constraint('fk_orden_descuento_autorizado_por', 'orden', type_='foreignkey')
    for col in ['propina', 'descuento_autorizado_por', 'descuento_motivo',
                'descuento_monto', 'descuento_pct', 'total', 'iva', 'subtotal']:
        op.drop_column('orden', col)

    op.alter_column('orden', 'monto_recibido',
                    type_=sa.Float(), existing_type=sa.Numeric(10, 2))
    op.alter_column('orden', 'cambio',
                    type_=sa.Float(), existing_type=sa.Numeric(10, 2))
