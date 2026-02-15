"""Agrega precio_unitario a OrdenDetalle y quita Enum de Sale.estado

Revision ID: c001_precio_unitario
Revises: a47b14dd3837
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c001_precio_unitario'
down_revision = 'a47b14dd3837'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar precio_unitario a orden_detalle
    op.add_column('orden_detalle',
                  sa.Column('precio_unitario', sa.Numeric(10, 2), nullable=True))

    # Poblar precio_unitario con el precio actual del producto para filas existentes
    op.execute("""
        UPDATE orden_detalle
        SET precio_unitario = (
            SELECT producto.precio FROM producto WHERE producto.id = orden_detalle.producto_id
        )
        WHERE precio_unitario IS NULL
    """)


def downgrade():
    op.drop_column('orden_detalle', 'precio_unitario')
