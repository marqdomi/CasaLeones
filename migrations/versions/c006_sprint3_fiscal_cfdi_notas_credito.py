"""Sprint 3: regimen_fiscal en clientes, forma_pago y facturapi_id en facturas, tabla notas_credito.

Revision ID: c006
Revises: c005
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'c006'
down_revision = 'c005'
branch_labels = None
depends_on = None


def upgrade():
    # --- Cliente: agregar regimen_fiscal ---
    op.add_column('clientes', sa.Column('regimen_fiscal', sa.String(5), nullable=True))

    # --- Factura: agregar forma_pago y facturapi_id ---
    op.add_column('facturas', sa.Column('forma_pago', sa.String(5), nullable=True))
    op.add_column('facturas', sa.Column('facturapi_id', sa.String(50), nullable=True))

    # --- Notas de crédito ---
    op.create_table(
        'notas_credito',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('factura_origen_id', sa.Integer, sa.ForeignKey('facturas.id'), nullable=False),
        sa.Column('uuid_cfdi', sa.String(40), nullable=True, unique=True),
        sa.Column('facturapi_id', sa.String(50), nullable=True),
        sa.Column('motivo', sa.String(200), nullable=False),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('iva', sa.Numeric(10, 2), nullable=False),
        sa.Column('monto', sa.Numeric(10, 2), nullable=False),
        sa.Column('estado', sa.String(20), server_default='pendiente'),
        sa.Column('xml_url', sa.String(500), nullable=True),
        sa.Column('pdf_url', sa.String(500), nullable=True),
        sa.Column('pac_response', sa.Text, nullable=True),
        sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('notas_credito')
    op.drop_column('facturas', 'facturapi_id')
    op.drop_column('facturas', 'forma_pago')
    op.drop_column('clientes', 'regimen_fiscal')
