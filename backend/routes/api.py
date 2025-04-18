from flask import Blueprint, jsonify, request
from models.models import Orden, OrdenDetalle
from models.database import db
from utils import obtener_ordenes_por_estacion, verificar_orden_completa

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/ordenes')
def listar_ordenes():
    estacion = request.args.get('estacion')
    estado = request.args.get('estado')
    if estacion:
        # Return map of orderId to list of detail dicts
        ordenes = obtener_ordenes_por_estacion(estacion)
        result = {
            oid: [d.to_dict() for d in detalles]
            for oid, detalles in ordenes.items()
        }
        return jsonify(result)
    elif estado:
        # Return list of orders with given estado
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
        return jsonify(result)
    else:
        return jsonify({'error': 'se requiere parámetro estacion o estado'}), 400

@api_bp.route('/ordenes/<int:orden_id>/detalles/<int:detalle_id>/listo', methods=['POST'])
def api_marcar_detalle_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    verificar_orden_completa(orden_id)
    return '', 204

@api_bp.route('/ordenes/<int:orden_id>/pagar', methods=['POST'])
def api_pagar_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    orden.estado = 'pagado'
    db.session.commit()
    return '', 204