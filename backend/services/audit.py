"""Sprint 6 — Item 3.5: Servicio de auditoría.

Registra acciones del sistema en la tabla audit_log para trazabilidad.
"""
import logging
from flask import request as flask_request, g

logger = logging.getLogger(__name__)


def registrar_auditoria(accion, entidad=None, entidad_id=None, descripcion=None, usuario_id=None):
    """Registra un evento de auditoría.

    Args:
        accion: Tipo de acción (login, logout, crear, editar, eliminar, pago, cancelar).
        entidad: Nombre del modelo afectado (Orden, Usuario, Producto, etc.).
        entidad_id: ID del registro afectado.
        descripcion: Detalle legible de la acción.
        usuario_id: ID del usuario. Si no se pasa, se toma de la sesión.
    """
    from backend.extensions import db
    from backend.models.models import AuditLog

    if usuario_id is None:
        from flask import session
        usuario_id = session.get('user_id')

    try:
        ip = flask_request.remote_addr if flask_request else None
        ua = str(flask_request.user_agent)[:300] if flask_request else None
    except RuntimeError:
        ip = None
        ua = None

    log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        descripcion=descripcion,
        ip_address=ip,
        user_agent=ua,
    )
    try:
        db.session.add(log)
        db.session.flush()
    except Exception:
        logger.exception('Error registrando auditoria: %s %s', accion, entidad)
