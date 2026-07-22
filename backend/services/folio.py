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


def _clave_sucursal(sucursal_id):
    """0 = sin sucursal. Ver el comentario del modelo: con NULL el UNIQUE no protege
    y se crean contadores duplicados."""
    return sucursal_id or 0


def _contador(sucursal_id, fecha):
    """Fila del contador del día, bloqueada para escritura.

    El bloqueo serializa a dos meseros que registran su primer producto al mismo
    tiempo; sin él, ambos leerían el mismo último folio.
    """
    clave = _clave_sucursal(sucursal_id)

    def _leer_bloqueado():
        return FolioDiario.query.filter_by(
            sucursal_id=clave, fecha=fecha,
        ).with_for_update().first()

    contador = _leer_bloqueado()
    if contador:
        return contador

    # Primera orden del día: crear el contador. Si otro proceso ganó la carrera, el
    # UNIQUE lo rechaza; se descarta el savepoint y se relee (ya lo tiene el otro).
    try:
        with db.session.begin_nested():
            db.session.add(FolioDiario(sucursal_id=clave, fecha=fecha, ultimo=0))
    except IntegrityError:
        pass  # otro proceso lo creó primero; se relee abajo, ya bloqueado por él
    contador = _leer_bloqueado()
    if contador is None:
        # No debería ocurrir: o lo creamos o lo creó el otro. Si pasa, es mejor un
        # error explícito que un AttributeError al incrementar.
        raise RuntimeError(
            f'No se pudo obtener el contador de folios (sucursal={clave}, fecha={fecha})')
    return contador


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
