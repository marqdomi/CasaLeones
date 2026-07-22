"""Folio diario por sucursal.

El `id` de Orden es una secuencia global compartida por todas las sucursales, y salta
cuando se descarta un borrador: al tercer día el cliente escucha "orden 247". El folio
reinicia cada día contable y se asigna cuando la orden deja de ser borrador.

Las órdenes anteriores se quedan sin folio: `Orden.numero` cae al `id` para ellas.

Idempotente: verifica con inspector antes de crear, para tolerar bases creadas por
create_all() con el modelo ya actualizado (flujo stamp head de update.sh).

Revision ID: c013
Revises: c012
Create Date: 2026-07-22
"""
import sqlalchemy as sa
from alembic import op

revision = 'c013'
down_revision = 'c012'
branch_labels = None
depends_on = None

_COLUMNAS = [
    ('folio', sa.Integer()),
    ('folio_fecha', sa.Date()),
]


def _inspector():
    return sa.inspect(op.get_bind())


def upgrade():
    insp = _inspector()

    if 'folios_diarios' not in insp.get_table_names():
        op.create_table(
            'folios_diarios',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('sucursal_id', sa.Integer(), sa.ForeignKey('sucursales.id'), nullable=True),
            sa.Column('fecha', sa.Date(), nullable=False),
            sa.Column('ultimo', sa.Integer(), nullable=False, server_default='0'),
            sa.UniqueConstraint('sucursal_id', 'fecha', name='uq_folio_sucursal_fecha'),
        )

    existentes = {c['name'] for c in insp.get_columns('orden')}
    for nombre, tipo in _COLUMNAS:
        if nombre not in existentes:
            op.add_column('orden', sa.Column(nombre, tipo, nullable=True))
            op.create_index(f'ix_orden_{nombre}', 'orden', [nombre], if_not_exists=True)


def downgrade():
    insp = _inspector()
    existentes = {c['name'] for c in insp.get_columns('orden')}
    for nombre, _ in _COLUMNAS:
        if nombre in existentes:
            op.drop_index(f'ix_orden_{nombre}', table_name='orden', if_exists=True)
            op.drop_column('orden', nombre)
    if 'folios_diarios' in insp.get_table_names():
        op.drop_table('folios_diarios')
