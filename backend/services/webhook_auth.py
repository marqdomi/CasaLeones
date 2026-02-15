"""Fase 5 — Sprint 1 (4.2): Verificación de firmas de webhooks de delivery."""
import hmac
import hashlib
import logging
from functools import wraps
from flask import request, jsonify, current_app

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Verificación por plataforma
# ---------------------------------------------------------------------------

def _verificar_uber_eats(req) -> bool:
    """Uber Eats envía HMAC-SHA256 en header X-Uber-Signature."""
    secret = current_app.config.get('UBER_EATS_WEBHOOK_SECRET', '')
    if not secret:
        return False
    signature = req.headers.get('X-Uber-Signature', '')
    if not signature:
        return False
    body = req.get_data()
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def _verificar_rappi(req) -> bool:
    """Rappi envía API key en header X-Rappi-API-Key."""
    expected_key = current_app.config.get('RAPPI_WEBHOOK_KEY', '')
    if not expected_key:
        return False
    provided_key = req.headers.get('X-Rappi-API-Key', '')
    return hmac.compare_digest(provided_key, expected_key)


def _verificar_didi_food(req) -> bool:
    """DiDi Food envía HMAC-SHA256 en header X-DiDi-Signature."""
    secret = current_app.config.get('DIDI_WEBHOOK_SECRET', '')
    if not secret:
        return False
    signature = req.headers.get('X-DiDi-Signature', '')
    if not signature:
        return False
    body = req.get_data()
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


_VERIFICADORES = {
    'uber_eats': _verificar_uber_eats,
    'rappi': _verificar_rappi,
    'didi_food': _verificar_didi_food,
}


# ---------------------------------------------------------------------------
# Decorator para aplicar en rutas de webhook
# ---------------------------------------------------------------------------

def verificar_webhook_signature(f):
    """Decorator que valida la firma del webhook según la plataforma.

    Si el secret no está configurado, el endpoint se desactiva (403).
    Si la firma es inválida, retorna 401.
    """
    @wraps(f)
    def wrapper(plataforma, *args, **kwargs):
        verificador = _VERIFICADORES.get(plataforma)
        if not verificador:
            return jsonify(error='Plataforma no soportada'), 400

        # Si no hay secret configurado, endpoint deshabilitado
        secrets_map = {
            'uber_eats': 'UBER_EATS_WEBHOOK_SECRET',
            'rappi': 'RAPPI_WEBHOOK_KEY',
            'didi_food': 'DIDI_WEBHOOK_SECRET',
        }
        secret_key = secrets_map.get(plataforma, '')
        secret_value = current_app.config.get(secret_key, '')
        if not secret_value:
            logger.warning(
                'Webhook %s rechazado: %s no configurado. IP=%s',
                plataforma, secret_key, request.remote_addr,
            )
            return jsonify(error=f'Webhook {plataforma} no habilitado (secret no configurado)'), 403

        if not verificador(request):
            logger.warning(
                'Webhook %s rechazado: firma inválida. IP=%s',
                plataforma, request.remote_addr,
            )
            return jsonify(error='Firma de webhook inválida'), 401

        return f(plataforma, *args, **kwargs)
    return wrapper
