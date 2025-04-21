from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from backend.models.models import Mesa, Orden, Producto, OrdenDetalle
import json
from backend.extensions import db
from backend.utils import login_required
from collections import defaultdict


meseros_bp = Blueprint('meseros', __name__)
print(">>> Cargando rutas de meseros desde:", __file__)
@meseros_bp.route('/meseros')
@login_required(rol='mesero')
def view_meseros():
    user_id = session.get('user_id')
    ordenes_mesero = Orden.query.filter_by(mesero_id=user_id).all()
    return render_template('meseros.html', ordenes_mesero=ordenes_mesero)

@meseros_bp.route('/crear_orden_para_llevar')
@login_required(rol='mesero')
def crear_orden_para_llevar():
    nueva_orden = Orden(mesero_id=session.get('user_id'), es_para_llevar=True, estado='pendiente')
    db.session.add(nueva_orden)
    db.session.commit()
    return redirect(url_for('meseros.detalle_orden', orden_id=nueva_orden.id))

@meseros_bp.route('/seleccionar_mesa', methods=['GET', 'POST'])
@login_required(rol='mesero')
def seleccionar_mesa():
    if request.method == 'POST':
        mesa_id = request.form.get('mesa_id')
        if mesa_id:
            nueva_orden = Orden(
                mesero_id=session.get('user_id'),
                mesa_id=int(mesa_id),
                es_para_llevar=False,
                estado='pendiente'
            )
            db.session.add(nueva_orden)
            db.session.commit()
            return redirect(url_for('meseros.detalle_orden', orden_id=nueva_orden.id))
        else:
            flash('Debes seleccionar una mesa.', 'warning')
            return redirect(url_for('meseros.seleccionar_mesa'))

    mesas = Mesa.query.all()
    return render_template('seleccionar_mesa.html', mesas=mesas)

@meseros_bp.route('/ordenes/<int:orden_id>/detalle')
@login_required(rol='mesero')
def detalle_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    productos = Producto.query.all()
    productos_por_categoria = defaultdict(list)
    for producto in productos:
        productos_por_categoria[producto.categoria.nombre].append(producto.to_dict())
    print(f"Renderizando orden #{orden.id} con productos agrupados por categoría.")
    return render_template('detalle_orden.html', orden=orden, productos_por_categoria=productos_por_categoria)

@meseros_bp.route('/ordenes/<int:orden_id>/detalle', methods=['POST'])
@login_required(rol='mesero')
def agregar_producto_orden(orden_id):
    data = request.form.get('productos_json')
    if not data:
        flash('No se recibieron productos.', 'warning')
        return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

    try:
        productos = json.loads(data)
        for p in productos:
            detalle = OrdenDetalle(
                orden_id=orden_id,
                producto_id=p['id'],
                cantidad=p['cantidad']
            )
            db.session.add(detalle)
        db.session.commit()
        flash('Productos agregados correctamente.', 'success')
    except Exception as e:
        flash(f'Error al procesar los productos: {str(e)}', 'danger')

    return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

@meseros_bp.route('/ordenes/<int:orden_id>/enviar_a_cocina', methods=['POST'])
@login_required(rol='mesero')
def enviar_orden_a_cocina(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    if orden.estado != 'pendiente':
        flash('La orden ya fue enviada o procesada.', 'warning')
    else:
        orden.estado = 'enviado'
        db.session.commit()
        flash('Orden enviada a cocina correctamente.', 'success')
    return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

@meseros_bp.route('/ordenes/<int:orden_id>/finalizar', methods=['POST'])
@login_required(rol='mesero')
def finalizar_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    if orden.estado != 'enviado':
        flash('Solo se pueden finalizar órdenes que hayan sido enviadas a cocina.', 'warning')
    else:
        orden.estado = 'finalizada'
        db.session.commit()
        flash('La orden ha sido finalizada correctamente.', 'success')
    return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

@meseros_bp.route('/ordenes/<int:orden_id>/cancelar', methods=['POST'])
@login_required(rol='mesero')
def cancelar_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    if orden.estado in ['finalizada', 'cancelada']:
        flash('La orden ya fue finalizada o cancelada previamente.', 'warning')
    else:
        orden.estado = 'cancelada'
        db.session.commit()
        flash('La orden ha sido cancelada correctamente.', 'success')
    return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

@meseros_bp.route('/ordenes/<int:orden_id>/pagar', methods=['POST'])
@login_required(rol='mesero')
def pagar_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    if orden.estado == 'pagado':
        flash('La orden ya está pagada.', 'warning')
    else:
        orden.estado = 'pagado'
        db.session.commit()
        flash('Orden marcada como pagada correctamente.', 'success')
    return redirect(url_for('meseros.view_meseros'))

@meseros_bp.route('/meseros/ordenes/<int:orden_id>/pago', methods=['GET'])
@login_required('mesero')
def pago_orden(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    detalles = OrdenDetalle.query.filter_by(orden_id=orden_id).all()
    total = sum(det.producto.precio * det.cantidad for det in detalles)
    return render_template('pago.html', orden=orden, detalles=detalles, total=total)