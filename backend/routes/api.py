from flask import Blueprint, request, jsonify
from backend.models.models import Orden, OrdenDetalle, Producto
from backend.extensions import db, socketio
from backend.utils import obtener_ordenes_por_estacion, verificar_orden_completa, login_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/ordenes', methods=['GET'])
@login_required()
def listar_ordenes():
    """
    Lista órdenes según estación o estado.
    """
    estacion = request.args.get('estacion')
    estado = request.args.get('estado')
    if estacion:
        ordenes = obtener_ordenes_por_estacion(estacion)
        result = []
        for oid, detalles in ordenes.items():
            result.append({
                'id': oid,
                'detalles': [
                    {
                        'id': d.id,
                        'producto_id': d.producto.id,
                        'producto_nombre': d.producto.nombre,
                        'cantidad': d.cantidad,
                        'notas': d.notas,
                        'estado': d.estado
                    } for d in detalles
                ]
            })
        return jsonify(result), 200
    elif estado:
        ordenes = Orden.query.filter_by(estado=estado).all()
        result = []
        for orden in ordenes:
            detalles = [
                {
                    'id': d.id,
                    'producto': {'nombre': d.producto.nombre}
                }
                for d in orden.detalles
            ]
            result.append({'id': orden.id, 'detalles': detalles})
        return jsonify(result), 200
    else:
        return jsonify({'error': 'se requiere parámetro estacion o estado'}), 400

@api_bp.route('/ordenes/<int:orden_id>/detalle/<int:detalle_id>/listo', methods=['POST'])
@login_required()
def marcar_detalle_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    verificar_orden_completa(orden_id)
    return jsonify({'message': 'Item marcado como listo.'}), 200

@api_bp.route('/ordenes/<int:orden_id>/pagar', methods=['POST'])
@login_required()
def pagar_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    orden.estado = 'pagado'
    db.session.commit()
    return jsonify({'message': 'Orden pagada.'}), 200

@api_bp.route('/ordenes/<int:orden_id>/detalle', methods=['GET', 'POST'])
@login_required()
def order_details(orden_id):
    if request.method == 'POST':
        data = request.get_json() or {}
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad', 1)
        notas = data.get('notas', '')

        producto = Producto.query.get_or_404(producto_id)
        orden = Orden.query.get_or_404(orden_id)

        detalle = OrdenDetalle(
            orden_id=orden.id,
            producto_id=producto.id,
            cantidad=cantidad,
            notas=notas,
            estado='pendiente',
            precio_unitario=producto.precio,
        )
        db.session.add(detalle)
        db.session.commit()

        socketio.emit('order_detail_added', {
            'orden_id': orden.id,
            'detalle': {
                'id': detalle.id,
                'producto_id': producto.id,
                'producto_nombre': producto.nombre,
                'cantidad': cantidad,
                'notas': notas,
                'estado': detalle.estado
            }
        })

        verificar_orden_completa(orden.id)

        # Return updated list of detalles
        detalles = OrdenDetalle.query.filter_by(orden_id=orden_id).all()
        out = [
            {
                'id': d.id,
                'producto_id': d.producto_id,
                'producto_nombre': d.producto.nombre,
                'cantidad': d.cantidad,
                'notas': d.notas,
                'estado': d.estado
            }
            for d in detalles
        ]
        return jsonify(out), 201

    # GET request
    detalles = OrdenDetalle.query.filter_by(orden_id=orden_id).all()
    out = [
        {
            'id': d.id,
            'producto_id': d.producto_id,
            'producto_nombre': d.producto.nombre,
            'cantidad': d.cantidad,
            'notas': d.notas,
            'estado': d.estado
        }
        for d in detalles
    ]
    return jsonify(out), 200


@api_bp.route('/ordenes/mesa/<int:mesa_id>')
@login_required()
def orden_activa_mesa(mesa_id):
    """Sprint 4 — 5.1: Retorna la orden activa de una mesa (para mapa de mesas)."""
    orden = Orden.query.filter(
        Orden.mesa_id == mesa_id,
        Orden.estado.notin_(['pagada', 'finalizada', 'cancelada']),
    ).first()
    if orden:
        return jsonify(orden_id=orden.id, estado=orden.estado)
    return jsonify(orden_id=None)
