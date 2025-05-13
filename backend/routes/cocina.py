from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify
from backend.models.models import Orden, OrdenDetalle
from backend.utils import login_required
from backend.utils import verificar_orden_completa
from backend.extensions import db
from backend.extensions import socketio
from datetime import date

cocina_bp = Blueprint('cocina', __name__, url_prefix='/cocina')

def obtener_ordenes_por_estacion(estacion_nombre):
    ordenes = Orden.query.filter(Orden.estado != 'pagado', Orden.estado != 'finalizada').all()
    ordenes_por_estacion = {
        orden.id: [
            detalle for detalle in orden.detalles
            if detalle.producto and detalle.producto.estacion and detalle.producto.estacion.nombre == estacion_nombre
        ]
        for orden in ordenes
    }
    return ordenes_por_estacion


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

@cocina_bp.route('/taqueros')
@login_required(roles='taquero')
def view_taqueros():
    ordenes_por_estacion = obtener_ordenes_por_estacion('taquero')
    return render_template('taqueros.html', ordenes_por_estacion=ordenes_por_estacion)

@cocina_bp.route('/comal')
@login_required(roles='comal')
def view_comal():
    ordenes_por_estacion = obtener_ordenes_por_estacion('comal')
    return render_template('Comal.html', ordenes_por_estacion=ordenes_por_estacion)

@cocina_bp.route('/bebidas')
@login_required(roles='mesero')
def view_bebidas():
    ordenes_por_estacion = obtener_ordenes_por_estacion('bebidas')
    return render_template('bebidas.html', ordenes_por_estacion=ordenes_por_estacion)

@cocina_bp.route('/bebidas/marcar/<int:orden_id>/<int:detalle_id>', methods=['POST'])
@login_required(roles='mesero')
def marcar_bebida_producto_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    verificar_orden_completa(orden_id)
    socketio.emit(
        'order_updated',
        {'orden_id': orden_id, 'detalle_id': detalle_id}
    )
    return jsonify({'message': 'Producto marcado como listo'}), 200

@cocina_bp.route('/taqueros/marcar/<int:orden_id>/<int:detalle_id>', methods=['POST'])
@login_required(roles='taquero')
def marcar_producto_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    verificar_orden_completa(orden_id)
    socketio.emit(
        'order_updated',
        {'orden_id': orden_id, 'detalle_id': detalle_id}
    )
    return jsonify({'message': 'Producto marcado como listo'}), 200

@cocina_bp.route('/comal/marcar/<int:orden_id>/<int:detalle_id>', methods=['POST'])
@login_required(roles='comal')
def marcar_comal_producto_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    verificar_orden_completa(orden_id)
    socketio.emit(
        'order_updated',
        {'orden_id': orden_id, 'detalle_id': detalle_id}
    )
    return jsonify({'message': 'Producto marcado como listo'}), 200

@cocina_bp.route('/historial')
@login_required(roles=['admin','superadmin'])
def historial_dia():
    hoy = date.today()
    ordenes = Orden.query.filter(
        db.func.date(Orden.timestamp) == hoy,
        Orden.estado.in_(['finalizada', 'pagada'])
    ).order_by(Orden.timestamp.desc()).all()
    
    return render_template('historial_dia.html', ordenes=ordenes)