from flask import Blueprint, request, jsonify, session, g, current_app
from backend.utils import login_required, verificar_orden_completa, verificar_stock_disponible
from backend.models.models import Orden, OrdenDetalle, Producto
from backend.extensions import db, socketio

orders_bp = Blueprint('orders', __name__, url_prefix='/api')

@orders_bp.route('/ordenes', methods=['POST'])
@login_required()
def create_order():
    data = request.get_json()
    es_para_llevar = data.get('es_para_llevar', False)
    mesa_id = data.get('mesa_id') if not es_para_llevar else None
    mesero_id = session.get('user_id')
    nueva_orden = Orden(mesa_id=mesa_id, mesero_id=mesero_id,
                        es_para_llevar=es_para_llevar,
                        sucursal_id=getattr(g, 'sucursal_id', None))
    db.session.add(nueva_orden)
    db.session.commit()
    socketio.emit('order_created', {
        'orden_id': nueva_orden.id,
        'estado': nueva_orden.estado,
        'es_para_llevar': nueva_orden.es_para_llevar,
        'tiempo_registro': nueva_orden.tiempo_registro.isoformat()
    })
    return jsonify({'message': 'Orden creada exitosamente.', 'orden_id': nueva_orden.id}), 201

@orders_bp.route('/ordenes/<int:orden_id>/estado', methods=['PUT'])
@login_required()
def update_order_status(orden_id):
    data = request.get_json()
    nuevo_estado = data.get('estado')
    if nuevo_estado not in ['lista', 'pagado']:
        return jsonify({'error': 'Estado no válido. Debe ser "lista" o "pagado".'}), 400
    orden = Orden.query.get_or_404(orden_id)
    orden.estado = nuevo_estado
    db.session.commit()
    socketio.emit('order_updated', {
        'orden_id': orden.id,
        'nuevo_estado': orden.estado
    })
    return jsonify({'message': 'Estado actualizado.', 'orden_id': orden.id}), 200

@orders_bp.route('/ordenes/<int:orden_id>/detalle', methods=['POST'])
@login_required()
def add_product_to_order(orden_id):
    data = request.get_json()
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)
    producto = Producto.query.get_or_404(producto_id)
    orden = Orden.query.get_or_404(orden_id)

    # Validación de stock (Sprint 2 — 3.2)
    if current_app.config.get('INVENTARIO_VALIDAR_STOCK'):
        disponible, faltantes, warns = verificar_stock_disponible(producto_id, cantidad)
        if not disponible:
            return jsonify({
                'error': 'Stock insuficiente',
                'faltantes': faltantes,
            }), 409

    detalle = OrdenDetalle(
        orden_id=orden.id,
        producto_id=producto.id,
        cantidad=cantidad,
        notas=data.get('notas', ''),
        precio_unitario=producto.precio,
    )
    db.session.add(detalle)
    db.session.commit()
    # Emit real-time update and check if order is now complete
    socketio.emit('order_detail_added', {
        'orden_id': orden.id,
        'detalle': {
            'id': detalle.id,
            'producto_id': producto.id,
            'producto_nombre': producto.nombre,
            'cantidad': cantidad,
            'notas': detalle.notas
        }
    })
    verificar_orden_completa(orden.id)
    return jsonify({
        'message': 'Producto agregado a la orden.',
        'detalle_id': detalle.id
    }), 201

@orders_bp.route('/ordenes/<int:orden_id>/detalle', methods=['GET'])
@login_required()
def get_order_details(orden_id):
    detalles = OrdenDetalle.query.filter_by(orden_id=orden_id).all()
    detalles_data = []
    for d in detalles:
        detalles_data.append({
            'id': d.id,
            'producto_id': d.producto_id,
            'producto_nombre': d.producto.nombre,
            'cantidad': d.cantidad,
            'notas': d.notas
        })
    return jsonify(detalles_data), 200