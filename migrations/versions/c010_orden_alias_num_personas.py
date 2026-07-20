"""Mesas compartidas: Orden.alias y Orden.num_personas.

Varias cuentas pueden convivir en una misma mesa; alias identifica al grupo
("los de la esquina") y num_personas cuántos comensales son.

Idempotente: verifica con inspector antes de agregar, para tolerar bases
creadas por create_all() con el modelo ya actualizado (flujo stamp head de
update.sh) sin fallar.

Revision ID: c010
Revises: c009
Create Date: 2026-07-20
"""
import sqlalchemy as sa
from alembic import op

revision = 'c010'
down_revision = 'c009'
branch_labels = None
depends_on = None

_COLUMNS = [
    ('alias', sa.String(50)),
    ('num_personas', sa.Integer()),
]


def _existing_columns():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {c['name'] for c in inspector.get_columns('orden')}


def upgrade():
    existentes = _existing_columns()
    for nombre, tipo in _COLUMNS:
        if nombre not in existentes:
            op.add_column('orden', sa.Column(nombre, tipo, nullable=True))


def downgrade():
    existentes = _existing_columns()
    for nombre, _ in _COLUMNS:
        if nombre in existentes:
            op.drop_column('orden', nombre)
