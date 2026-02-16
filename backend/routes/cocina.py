import logging
from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify
from backend.models.models import Orden, OrdenDetalle, Producto, Estacion
from backend.utils import login_required, verificar_orden_completa
from backend.extensions import db, socketio
from flask_login import current_user
from datetime import date

logger = logging.getLogger(__name__)

cocina_bp = Blueprint('cocina', __name__, url_prefix='/cocina')

# ── Station config ──────────────────────────────────────────────
STATION_CONFIG = {
    'taqueros': {
        'estacion_db': 'taquero',
        'label': 'Taqueros',
        'color': 'var(--cl-red-500)',
        'roles_view': ['taquero', 'admin', 'superadmin'],
        'roles_marcar': ['taquero'],
    },
    'comal': {
        'estacion_db': 'comal',
        'label': 'Comal',
        'color': 'var(--cl-amber-500, #f59e0b)',
        'roles_view': ['comal', 'admin', 'superadmin'],
        'roles_marcar': ['comal'],
    },
    'bebidas': {
        'estacion_db': 'bebidas',
        'label': 'Bebidas',
        'color': 'var(--cl-blue-500, #3b82f6)',
        'roles_view': ['mesero', 'bebidas', 'admin', 'superadmin'],
        'roles_marcar': ['mesero', 'bebidas'],
    },
}


def _query_pending_detalles(estacion_nombre):
    """Return pending OrdenDetalle items for a given station."""
    return OrdenDetalle.query \
        .join(Orden, OrdenDetalle.orden_id == Orden.id) \
        .join(Producto, OrdenDetalle.producto_id == Producto.id) \
        .join(Estacion, Producto.estacion_id == Estacion.id) \
        .filter(
            Estacion.nombre == estacion_nombre,
            OrdenDetalle.estado == 'pendiente',
            Orden.estado.in_(['enviado', 'en_preparacion', 'recibido', 'lista_para_entregar'])
        ) \
        .order_by(Orden.tiempo_registro.asc(), OrdenDetalle.id.asc()).all()


def _group_by_orden(detalles):
    """Group a flat list of OrdenDetalle into {Orden: [detalles]} dict."""
    grouped = {}
    for d in detalles:
        grouped.setdefault(d.orden, []).append(d)
    return grouped


def _marcar_listo(orden_id, detalle_id):
    """Mark a single OrdenDetalle as 'listo' and emit Socket.IO event."""
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    verificar_orden_completa(orden_id)
    socketio.emit('item_listo_notificacion', {
        'item_id': detalle.id,
        'orden_id': orden_id,
        'producto_id': detalle.producto_id,
        'producto_nombre': detalle.producto.nombre,
        'mesa_nombre': detalle.orden.mesa.numero if detalle.orden.mesa else 'Para Llevar',
        'mensaje': f'¡{detalle.producto.nombre} de la orden {orden_id} está listo!'
    })
    return jsonify({'message': 'Producto marcado como listo'}), 200


# ── API endpoint ────────────────────────────────────────────────
@cocina_bp.route('/api/orders')
@login_required(roles=['taquero', 'comal', 'bebidas', 'admin', 'superadmin'])
def api_orders():
    ordenes = Orden.query.filter(Orden.estado != 'pagado', Orden.estado != 'finalizada').all()
    return jsonify([{
        'id': o.id, 'estado': o.estado,
        'tiempo_registro': o.tiempo_registro.isoformat()
    } for o in ordenes]), 200


# ── Station views (unified) ────────────────────────────────────
@cocina_bp.route('/taqueros', endpoint='dashboard_taqueros_view')
@login_required(roles='taquero')
def view_taqueros():
    cfg = STATION_CONFIG['taqueros']
    detalles = _query_pending_detalles(cfg['estacion_db'])
    ordenes_data = _group_by_orden(detalles)
    return render_template('kds_station.html',
                           ordenes_data=ordenes_data,
                           station='taqueros', cfg=cfg)


@cocina_bp.route('/comal', endpoint='dashboard_comal_view')
@login_required(roles='comal')
def view_comal():
    cfg = STATION_CONFIG['comal']
    detalles = _query_pending_detalles(cfg['estacion_db'])
    ordenes_data = _group_by_orden(detalles)
    return render_template('kds_station.html',
                           ordenes_data=ordenes_data,
                           station='comal', cfg=cfg)


@cocina_bp.route('/bebidas', endpoint='dashboard_bebidas_view')
@login_required(roles=['mesero', 'bebidas', 'admin', 'superadmin'])
def view_bebidas():
    cfg = STATION_CONFIG['bebidas']
    detalles = _query_pending_detalles(cfg['estacion_db'])
    ordenes_data = _group_by_orden(detalles)
    return render_template('kds_station.html',
                           ordenes_data=ordenes_data,
                           station='bebidas', cfg=cfg)


# ── Fragment endpoints (AJAX refresh) ──────────────────────────
@cocina_bp.route('/taquero/fragmento_ordenes', endpoint='fragmento_ordenes_taquero_view')
@login_required(roles=['taquero', 'admin', 'superadmin'])
def fragmento_ordenes_taquero():
    return _fragmento('taquero')


@cocina_bp.route('/comal/fragmento_ordenes', endpoint='fragmento_ordenes_comal_view')
@login_required(roles=['comal', 'admin', 'superadmin'])
def fragmento_ordenes_comal():
    return _fragmento('comal')


@cocina_bp.route('/bebidas/fragmento_ordenes', endpoint='fragmento_ordenes_bebidas_view')
@login_required(roles=['mesero', 'bebidas', 'admin', 'superadmin'])
def fragmento_ordenes_bebidas():
    return _fragmento('bebidas')


def _fragmento(estacion_nombre):
    """Return JSON with rendered HTML fragment + count for a station."""
    detalles = _query_pending_detalles(estacion_nombre)
    ordenes_data = _group_by_orden(detalles)
    total = sum(d.cantidad for d in detalles)
    html = render_template('cocina/_kds_cards_fragment.html', ordenes_data=ordenes_data)
    return jsonify({'html': html, 'conteo_productos': total})


# ── Mark-done endpoints ────────────────────────────────────────
@cocina_bp.route('/taqueros/marcar/<int:orden_id>/<int:detalle_id>',
                  methods=['POST'], endpoint='marcar_taqueros_listo_view')
@login_required(roles='taquero')
def marcar_taqueros(orden_id, detalle_id):
    return _marcar_listo(orden_id, detalle_id)


@cocina_bp.route('/comal/marcar/<int:orden_id>/<int:detalle_id>',
                  methods=['POST'], endpoint='marcar_comal_listo_view')
@login_required(roles='comal')
def marcar_comal(orden_id, detalle_id):
    return _marcar_listo(orden_id, detalle_id)


@cocina_bp.route('/bebidas/marcar/<int:orden_id>/<int:detalle_id>',
                  methods=['POST'], endpoint='marcar_bebida_listo_view')
@login_required(roles=['mesero', 'bebidas'])
def marcar_bebidas(orden_id, detalle_id):
    return _marcar_listo(orden_id, detalle_id)


# ── Historial ──────────────────────────────────────────────────
@cocina_bp.route('/historial')
@login_required(roles=['admin', 'superadmin'])
def historial_dia():
    hoy = date.today()
    ordenes = Orden.query.filter(
        db.func.date(Orden.tiempo_registro) == hoy,
        Orden.estado.in_(['finalizada', 'pagada'])
    ).order_by(Orden.tiempo_registro.desc()).all()

    return render_template('historial_dia.html', ordenes=ordenes)
