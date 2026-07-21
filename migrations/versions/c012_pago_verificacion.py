"""Verificación de pagos: transferencias confirmadas contra el banco.

El efectivo se verifica solo (está en la mano), pero una transferencia hay que
confirmarla en la app del banco antes de dar la cuenta por pagada. Un pago sin
verificar no cubre la cuenta y no la cierra.

Los pagos ya existentes quedan como verificados: son efectivo histórico.

Idempotente: verifica con inspector antes de agregar, para tolerar bases creadas por
create_all() con el modelo ya actualizado (flujo stamp head de update.sh).

Revision ID: c012
Revises: c011
Create Date: 2026-07-21
"""
import sqlalchemy as sa
from alembic import op

revision = 'c012'
down_revision = 'c011'
branch_labels = None
depends_on = None

_COLUMNS = [
    ('verificado', sa.Boolean(), {'nullable': False, 'server_default': sa.true()}),
    ('verificado_por', sa.Integer(), {'nullable': True}),
    ('fecha_verificacion', sa.DateTime(), {'nullable': True}),
]


def _existing_columns():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {c['name'] for c in inspector.get_columns('pagos')}


def upgrade():
    existentes = _existing_columns()
    for nombre, tipo, kwargs in _COLUMNS:
        if nombre not in existentes:
            op.add_column('pagos', sa.Column(nombre, tipo, **kwargs))
    if 'verificado' not in existentes:
        op.create_index('ix_pagos_verificado', 'pagos', ['verificado'], if_not_exists=True)


def downgrade():
    existentes = _existing_columns()
    op.drop_index('ix_pagos_verificado', table_name='pagos', if_exists=True)
    for nombre, _, _ in _COLUMNS:
        if nombre in existentes:
            op.drop_column('pagos', nombre)
