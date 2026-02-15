"""Sprint 6 — Item 3.5: Rutas de auditoría."""
import logging
from datetime import date
from flask import Blueprint, render_template, request
from backend.utils import login_required
from backend.extensions import db
from backend.models.models import AuditLog, Usuario
from sqlalchemy import func
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

auditoria_bp = Blueprint('auditoria', __name__, url_prefix='/admin/auditoria')


@auditoria_bp.route('/')
@login_required(roles=['superadmin'])
def lista_auditoria():
    fi = request.args.get('fecha_inicio', date.today().isoformat())
    ff = request.args.get('fecha_fin', date.today().isoformat())
    accion_filtro = request.args.get('accion', '')
    entidad_filtro = request.args.get('entidad', '')
    page = request.args.get('page', 1, type=int)

    q = AuditLog.query.options(joinedload(AuditLog.usuario))

    q = q.filter(
        func.date(AuditLog.fecha) >= date.fromisoformat(fi),
        func.date(AuditLog.fecha) <= date.fromisoformat(ff),
    )

    if accion_filtro:
        q = q.filter(AuditLog.accion == accion_filtro)
    if entidad_filtro:
        q = q.filter(AuditLog.entidad == entidad_filtro)

    pagination = q.order_by(AuditLog.fecha.desc()).paginate(page=page, per_page=50, error_out=False)

    # Distinct actions and entities for filters
    acciones = [r[0] for r in db.session.query(AuditLog.accion).distinct().order_by(AuditLog.accion).all()]
    entidades = [r[0] for r in db.session.query(AuditLog.entidad).distinct().order_by(AuditLog.entidad).all() if r[0]]

    return render_template('admin/auditoria/lista.html',
                           logs=pagination.items, pagination=pagination,
                           fecha_inicio=fi, fecha_fin=ff,
                           accion_filtro=accion_filtro, entidad_filtro=entidad_filtro,
                           acciones=acciones, entidades=entidades)
