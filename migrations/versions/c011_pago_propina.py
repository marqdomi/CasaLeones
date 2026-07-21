"""Pago.propina: propina atribuida a cada pago.

Sin esto la propina sólo vive en Orden y no se sabe por qué método entró, así que el
corte no puede decir cuánto efectivo debería haber físicamente en la caja: el arqueo
salía "sobrado" justo por el monto de las propinas en efectivo.

Idempotente: verifica con inspector antes de agregar, para tolerar bases creadas por
create_all() con el modelo ya actualizado (flujo stamp head de update.sh).

Revision ID: c011
Revises: c010
Create Date: 2026-07-21
"""
import sqlalchemy as sa
from alembic import op

revision = 'c011'
down_revision = 'c010'
branch_labels = None
depends_on = None


def _existing_columns():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {c['name'] for c in inspector.get_columns('pagos')}


def upgrade():
    if 'propina' not in _existing_columns():
        op.add_column('pagos', sa.Column('propina', sa.Numeric(10, 2),
                                         nullable=False, server_default='0'))


def downgrade():
    if 'propina' in _existing_columns():
        op.drop_column('pagos', 'propina')
