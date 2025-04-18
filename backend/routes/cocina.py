from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify
from models.models import Orden, OrdenDetalle
from utils import login_required
from models.database import db

cocina_bp = Blueprint('cocina', __name__, url_prefix='/cocina')

def obtener_ordenes_por_estacion(estacion_nombre):
    ordenes = Orden.query.filter(Orden.estado != 'pagado').all()
    ordenes_por_estacion = {
        orden.id: [
            detalle for detalle in orden.detalles
            if detalle.producto and detalle.producto.estacion and detalle.producto.estacion.nombre == estacion_nombre
        ]
        for orden in ordenes
    }
    return ordenes_por_estacion

@cocina_bp.route('/')
@login_required(rol='admin')
def view_cocina():
    ordenes_cocina = Orden.query.filter(Orden.estado != 'pagado').all()
    ordenes_por_estacion = obtener_ordenes_por_estacion('taquero')
    return render_template(
        'taqueros.html',
        ordenes_por_estacion=ordenes_por_estacion   # exactamente este nombre
    )

@cocina_bp.route('/api/orders')
@login_required(rol='taquero')
def api_orders():
    ordenes = Orden.query.filter(Orden.estado != 'pagado').all()
    orders_data = [{
        'id': orden.id,
        'estado': orden.estado,
        'tiempo_registro': orden.tiempo_registro.isoformat()
    } for orden in ordenes]
    return jsonify(orders_data), 200

@cocina_bp.route('/taqueros')
@login_required(rol='taquero')
def view_taqueros():
    ordenes_por_estacion = obtener_ordenes_por_estacion('taquero')
    return render_template('taqueros.html', ordenes_por_estacion=ordenes_por_estacion)

@cocina_bp.route('/comal')
@login_required(rol='comal')
def view_comal():
    ordenes_por_estacion = obtener_ordenes_por_estacion('comal')
    return render_template('Comal.html', ordenes_por_estacion=ordenes_por_estacion)

@cocina_bp.route('/bebidas')
@login_required(rol='bebidas')
def view_bebidas():
    ordenes_por_estacion = obtener_ordenes_por_estacion('bebidas')
    return render_template('bebidas.html', ordenes_por_estacion=ordenes_por_estacion)

@cocina_bp.route('/bebidas/marcar/<int:orden_id>/<int:detalle_id>', methods=['POST'])
@login_required(rol='bebidas')
def marcar_bebida_producto_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    flash('Producto de Bebidas marcado como listo', 'success')
    return redirect(url_for('cocina.view_bebidas'))

@cocina_bp.route('/taqueros/marcar/<int:orden_id>/<int:detalle_id>', methods=['POST'])
@login_required(rol='taquero')
def marcar_producto_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    flash('Producto marcado como listo', 'success')
    return redirect(url_for('cocina.view_taqueros'))

@cocina_bp.route('/comal/marcar/<int:orden_id>/<int:detalle_id>', methods=['POST'])
@login_required(rol='comal')
def marcar_comal_producto_listo(orden_id, detalle_id):
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    detalle.estado = 'listo'
    db.session.commit()
    flash('Producto marcado como listo', 'success')
    return redirect(url_for('cocina.view_comal'))