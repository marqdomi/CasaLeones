import logging
from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify
from backend.models.models import Orden, OrdenDetalle, Producto, Estacion
from backend.utils import login_required, verificar_orden_completa
from backend.extensions import db, socketio
from flask_login import current_user
from datetime import date

logger = logging.getLogger(__name__)

cocina_bp = Blueprint('cocina', __name__, url_prefix='/cocina')


def obtener_ordenes_por_estacion(estacion_nombre):
    ordenes = Orden.query.filter(Orden.estado != 'pagado', Orden.estado != 'finalizada').all()
    return {
        orden.id: [
            detalle for detalle in orden.detalles
            if detalle.producto and detalle.producto.estacion
            and detalle.producto.estacion.nombre == estacion_nombre
        ]
        for orden in ordenes
    }


@cocina_bp.route('/api/orders')
@login_required(roles='taquero')
def api_orders():
    ordenes = Orden.query.filter(Orden.estado != 'pagado', Orden.estado != 'finalizada').all()
    orders_data = [{
        'id': orden.id,
        'estado': orden.estado,
        'tiempo_registro': orden.tiempo_registro.isoformat()
    } for orden in ordenes]
    return jsonify(orders_data), 200


@cocina_bp.route('/taqueros', endpoint='dashboard_taqueros_view')
@login_required(roles='taquero')
def view_taqueros():
    ordenes_por_estacion = obtener_ordenes_por_estacion('taquero')
    return render_template('taqueros.html', ordenes_por_estacion=ordenes_por_estacion)


@cocina_bp.route('/taquero/fragmento_ordenes', endpoint='fragmento_ordenes_taquero_view')
@login_required(roles=['taquero', 'admin', 'superadmin'])
def fragmento_ordenes_taquero():
    detalles_pendientes_estacion = OrdenDetalle.query \
        .join(Orden, OrdenDetalle.orden_id == Orden.id) \
        .join(Producto, OrdenDetalle.producto_id == Producto.id) \
        .join(Estacion, Producto.estacion_id == Estacion.id) \
        .filter(
            Estacion.nombre == 'taquero',
            OrdenDetalle.estado == 'pendiente',
            Orden.estado.in_(['enviado', 'en_preparacion', 'recibido', 'lista_para_entregar'])
        ) \
        .order_by(Orden.tiempo_registro.asc(), OrdenDetalle.id.asc()).all()

    ordenes_con_items_pendientes = {}
    for detalle in detalles_pendientes_estacion:
        ordenes_con_items_pendientes.setdefault(detalle.orden, []).append(detalle)

    total_productos_fisicos_pendientes = sum(d.cantidad for d in detalles_pendientes_estacion)
    html_fragmento = render_template('cocina/_ordenes_agrupadas_cards.html',
                                     ordenes_data=ordenes_con_items_pendientes)
    return jsonify({
        'html': html_fragmento,
        'conteo_productos': total_productos_fisicos_pendientes
    })


@cocina_bp.route('/comal', endpoint='dashboard_comal_view')
@login_required(roles='comal')
def view_comal():
    detalles_pendientes = OrdenDetalle.query \
        .join(Orden, OrdenDetalle.orden_id == Orden.id) \
        .join(Producto, OrdenDetalle.producto_id == Producto.id) \
        .join(Estacion, Producto.estacion_id == Estacion.id) \
        .filter(
            Estacion.nombre == 'comal',
            OrdenDetalle.estado == 'pendiente',
            Orden.estado.in_(['enviado', 'en_preparacion', 'recibido', 'lista_para_entregar'])
        ) \
        .order_by(Orden.tiempo_registro.asc(), OrdenDetalle.id.asc()).all()

    ordenes_data = {}
    for det in detalles_pendientes:
        ordenes_data.setdefault(det.orden, []).append(det)

    return render_template('Comal.html', ordenes_data=ordenes_data)


@cocina_bp.route('/comal/fragmento_ordenes', endpoint='fragmento_ordenes_comal_view')
@login_required(roles=['comal', 'admin', 'superadmin'])
def fragmento_ordenes_comal():
    detalles_pendientes_estacion = OrdenDetalle.query \
        .join(Orden, OrdenDetalle.orden_id == Orden.id) \
        .join(Producto, OrdenDetalle.producto_id == Producto.id) \
        .join(Estacion, Producto.estacion_id == Estacion.id) \
        .filter(
            Estacion.nombre == 'comal',
            OrdenDetalle.estado == 'pendiente',
            Orden.estado.in_(['enviado', 'en_preparacion', 'recibido', 'lista_para_entregar'])
        ) \
        .order_by(Orden.tiempo_registro.asc(), OrdenDetalle.id.asc()).all()

    ordenes_con_items_pendientes = {}
    for detalle in detalles_pendientes_estacion:
        ordenes_con_items_pendientes.setdefault(detalle.orden, []).append(detalle)

    total_productos_fisicos_pendientes = sum(d.cantidad for d in detalles_pendientes_estacion)
    html_fragmento = render_template('cocina/_ordenes_agrupadas_cards.html',
                                     ordenes_data=ordenes_con_items_pendientes)
    return jsonify({
        'html': html_fragmento,
        'conteo_productos': total_productos_fisicos_pendientes
    })


@cocina_bp.route('/bebidas', endpoint='dashboard_bebidas_view')
@login_required(roles=['mesero', 'bebidas', 'admin', 'superadmin'])
def view_bebidas():
    detalles_pendientes = OrdenDetalle.query \
        .join(Orden, OrdenDetalle.orden_id == Orden.id) \
        .join(Producto, OrdenDetalle.producto_id == Producto.id) \
        .join(Estacion, Producto.estacion_id == Estacion.id) \
        .filter(
            Estacion.nombre == 'bebidas',
            OrdenDetalle.estado == 'pendiente',
            Orden.estado.in_(['enviado', 'en_preparacion', 'recibido', 'lista_para_entregar'])
        ) \
        .order_by(Orden.tiempo_registro.asc(), OrdenDetalle.id.asc()).all()

    ordenes_data = {}
    for det in detalles_pendientes:
        ordenes_data.setdefault(det.orden, []).append(det)

    return render_template('bebidas.html', ordenes_data=ordenes_data)


@cocina_bp.route('/bebidas/fragmento_ordenes', endpoint='fragmento_ordenes_bebidas_view')
@login_required(roles=['mesero', 'bebidas', 'admin', 'superadmin'])
def fragmento_ordenes_bebidas():
    detalles_pendientes_estacion = OrdenDetalle.query \
        .join(Orden, OrdenDetalle.orden_id == Orden.id) \
        .join(Producto, OrdenDetalle.producto_id == Producto.id) \
        .join(Estacion, Producto.estacion_id == Estacion.id) \
        .filter(
            Estacion.nombre == 'bebidas',
            OrdenDetalle.estado == 'pendiente',
            Orden.estado.in_(['enviado', 'en_preparacion', 'recibido', 'lista_para_entregar'])
        ) \
        .order_by(Orden.tiempo_registro.asc(), OrdenDetalle.id.asc()).all()

    ordenes_con_items_pendientes = {}
    for detalle in detalles_pendientes_estacion:
        ordenes_con_items_pendientes.setdefault(detalle.orden, []).append(detalle)

    total_productos_fisicos_pendientes = sum(d.cantidad for d in detalles_pendientes_estacion)
    html_fragmento = render_template('cocina/_ordenes_agrupadas_cards.html',
                                     ordenes_data=ordenes_con_items_pendientes)
    return jsonify({
        'html': html_fragmento,
        'conteo_productos': total_productos_fisicos_pendientes
    })


@cocina_bp.route('/bebidas/marcar/<int:orden_id>/<int:detalle_id>',
                  methods=['POST'], endpoint='marcar_bebida_listo_view')
@login_required(roles='mesero')
def marcar_bebida_producto_listo(orden_id, detalle_id):
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


@cocina_bp.route('/taqueros/marcar/<int:orden_id>/<int:detalle_id>',
                  methods=['POST'], endpoint='marcar_taqueros_listo_view')
@login_required(roles='taquero')
def marcar_producto_listo(orden_id, detalle_id):
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


@cocina_bp.route('/comal/marcar/<int:orden_id>/<int:detalle_id>',
                  methods=['POST'], endpoint='marcar_comal_listo_view')
@login_required(roles='comal')
def marcar_comal_producto_listo(orden_id, detalle_id):
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


@cocina_bp.route('/historial')
@login_required(roles=['admin', 'superadmin'])
def historial_dia():
    hoy = date.today()
    ordenes = Orden.query.filter(
        db.func.date(Orden.tiempo_registro) == hoy,
        Orden.estado.in_(['finalizada', 'pagada'])
    ).order_by(Orden.tiempo_registro.desc()).all()

    return render_template('historial_dia.html', ordenes=ordenes)
