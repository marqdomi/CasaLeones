"""Folio diario por sucursal.

El `id` de Orden es una secuencia global compartida por todas las sucursales, y además
salta cuando se descarta un borrador: al tercer día el cliente escucha "orden 247". El
folio reinicia cada día contable, así que "orden 7" es la séptima cuenta real del día.

Se asigna cuando la orden deja de ser borrador (su primer producto), no al crearla:
un borrador abandonado no debe quemar un número.
"""
import logging

from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models.models import FolioDiario
from backend.services.tiempo import hoy_local

logger = logging.getLogger(__name__)


def _contador(sucursal_id, fecha):
    """Fila del contador del día, bloqueada para escritura.

    El bloqueo serializa a dos meseros que registran su primer producto al mismo
    tiempo; sin él, ambos leerían el mismo último folio.
    """
    contador = FolioDiario.query.filter_by(
        sucursal_id=sucursal_id, fecha=fecha,
    ).with_for_update().first()
    if contador:
        return contador

    # Primera orden del día: crear el contador. Si otro proceso ganó la carrera, el
    # UNIQUE lo rechaza y se relee (ya bloqueado por el otro).
    try:
        with db.session.begin_nested():
            contador = FolioDiario(sucursal_id=sucursal_id, fecha=fecha, ultimo=0)
            db.session.add(contador)
        return FolioDiario.query.filter_by(
            sucursal_id=sucursal_id, fecha=fecha,
        ).with_for_update().first()
    except IntegrityError:
        return FolioDiario.query.filter_by(
            sucursal_id=sucursal_id, fecha=fecha,
        ).with_for_update().first()


def asignar_folio(orden):
    """Le pone folio del día a la orden si aún no tiene. Devuelve el folio.

    Idempotente: si la orden ya tiene folio no lo cambia (agregar un segundo producto
    no debe renumerarla).
    """
    if orden.folio:
        return orden.folio

    fecha = hoy_local()
    contador = _contador(orden.sucursal_id, fecha)
    contador.ultimo += 1
    orden.folio = contador.ultimo
    orden.folio_fecha = fecha
    logger.info('Folio %s asignado a orden id=%s (sucursal=%s, %s)',
                orden.folio, orden.id, orden.sucursal_id, fecha)
    return orden.folio
