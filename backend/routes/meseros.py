from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from backend.models.models import Mesa, Orden, Producto, OrdenDetalle, Sale, SaleItem, Usuario # Añadido Usuario
import json
from backend.extensions import db, socketio
from backend.utils import login_required # Tu decorador
from collections import defaultdict
from sqlalchemy.orm import joinedload
from datetime import datetime

meseros_bp = Blueprint('meseros', __name__, url_prefix='/meseros') # Añadido url_prefix

# (Quité el print global, es mejor para producción)
# print(">>> Cargando rutas de meseros desde:", __file__)

@meseros_bp.route('/') # Ruta para el dashboard principal de meseros
@login_required(roles='mesero')
def view_meseros():
    user_id = session.get('user_id')
    # Eager load relaciones para evitar N+1 queries en la plantilla
    ordenes_mesero = Orden.query.options(
        joinedload(Orden.mesa), # Para acceder a orden.mesa.numero
        joinedload(Orden.detalles).joinedload(OrdenDetalle.producto) # Para detalles y sus productos
    ).filter(
        Orden.mesero_id == user_id,
        Orden.estado.notin_(['pagada', 'finalizada', 'cancelada']) # Excluir canceladas también
    ).order_by(Orden.tiempo_registro.desc()).all() # Ordenar por más recientes primero
    
    return render_template('meseros.html', ordenes_mesero=ordenes_mesero)

@meseros_bp.route('/crear_orden_para_llevar')
@login_required(roles='mesero')
def crear_orden_para_llevar():
    nueva_orden = Orden(
        mesero_id=session.get('user_id'), 
        es_para_llevar=True, 
        estado='pendiente' # Estado inicial al crear
    )
    db.session.add(nueva_orden)
    db.session.commit()
    flash('Nueva orden para llevar creada. Añade productos.', 'success')
    return redirect(url_for('meseros.detalle_orden', orden_id=nueva_orden.id))

@meseros_bp.route('/seleccionar_mesa', methods=['GET', 'POST'])
@login_required(roles='mesero')
def seleccionar_mesa():
    if request.method == 'POST':
        mesa_id = request.form.get('mesa_id')
        if mesa_id:
            # Verificar si la mesa ya tiene una orden activa no pagada (opcional, pero buena práctica)
            orden_existente = Orden.query.filter(
                Orden.mesa_id == int(mesa_id),
                Orden.estado.notin_(['pagada', 'finalizada', 'cancelada'])
            ).first()
            if orden_existente:
                flash(f'La Mesa {Mesa.query.get(int(mesa_id)).numero} ya tiene una orden activa (ID: {orden_existente.id}). Puedes modificarla.', 'warning')
                return redirect(url_for('meseros.detalle_orden', orden_id=orden_existente.id))

            nueva_orden = Orden(
                mesero_id=session.get('user_id'),
                mesa_id=int(mesa_id),
                es_para_llevar=False,
                estado='pendiente' # Estado inicial al crear
            )
            db.session.add(nueva_orden)
            db.session.commit()
            flash(f'Nueva orden creada para Mesa {nueva_orden.mesa.numero}. Añade productos.', 'success')
            return redirect(url_for('meseros.detalle_orden', orden_id=nueva_orden.id))
        else:
            flash('Debes seleccionar una mesa.', 'warning')
            return redirect(url_for('meseros.seleccionar_mesa'))

    mesas = Mesa.query.order_by(Mesa.numero).all() # Asumiendo que quieres ordenarlas
    return render_template('seleccionar_mesa.html', mesas=mesas)

@meseros_bp.route('/ordenes/<int:orden_id>/detalle_orden', methods=['GET']) # Cambiado nombre de endpoint para evitar colisión
@login_required(roles='mesero')
def detalle_orden(orden_id): # Esta es la página para AÑADIR/MODIFICAR productos a una orden
    orden = Orden.query.options(
        joinedload(Orden.mesa),
        joinedload(Orden.detalles).joinedload(OrdenDetalle.producto)
    ).get_or_404(orden_id)

    # No permitir modificar si ya fue enviada, pagada, etc.
    if orden.estado not in ['pendiente']:
        flash(f'La orden #{orden.id} ya fue procesada ({orden.estado}) y no puede modificarse aquí.', 'warning')
        return redirect(url_for('meseros.view_meseros'))

    productos = Producto.query.options(joinedload(Producto.categoria)).order_by(Producto.categoria_id, Producto.nombre).all()
    productos_por_categoria = defaultdict(list)
    for producto in productos:
        productos_por_categoria[producto.categoria.nombre].append(producto.to_dict())
    
    return render_template('detalle_orden.html', orden=orden, productos_por_categoria=productos_por_categoria)

@meseros_bp.route('/ordenes/<int:orden_id>/agregar_productos', methods=['POST']) # Cambiado nombre de endpoint
@login_required(roles='mesero')
def agregar_productos_a_orden(orden_id): # Cambiado nombre de función
    orden = Orden.query.get_or_404(orden_id)
    if orden.estado != 'pendiente':
        flash(f'No se pueden agregar productos. La orden #{orden.id} ya fue procesada ({orden.estado}).', 'danger')
        return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

    data = request.form.get('productos_json')
    if not data:
        flash('No se recibieron productos.', 'warning')
        return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

    try:
        productos_seleccionados = json.loads(data)
        if not productos_seleccionados:
            flash('No se seleccionaron productos para agregar.', 'info')
            return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))

        for p_data in productos_seleccionados:
            producto_obj = Producto.query.get(p_data['id'])
            if not producto_obj:
                flash(f"Producto con ID {p_data['id']} no encontrado.", 'danger')
                continue 
            
            # Verificar si ya existe un detalle para este producto en esta orden (para agrupar o añadir nuevo)
            detalle_existente = OrdenDetalle.query.filter_by(orden_id=orden_id, producto_id=producto_obj.id).first()
            if detalle_existente: # Si ya existe, actualiza la cantidad
                 detalle_existente.cantidad += int(p_data['cantidad'])
            else: # Si no existe, crea un nuevo detalle
                detalle = OrdenDetalle(
                    orden_id=orden_id,
                    producto_id=producto_obj.id,
                    cantidad=int(p_data['cantidad']),
                    # precio_unitario se podría guardar aquí si los precios pueden cambiar,
                    # pero tu modelo no lo tiene. Asume que se toma de Producto.precio
                    estado='pendiente' # Estado inicial del detalle
                )
                db.session.add(detalle)
        db.session.commit()
        flash('Productos agregados/actualizados correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar los productos: {str(e)}', 'danger')

    return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))


@meseros_bp.route('/ordenes/<int:orden_id>/enviar_a_cocina', methods=['POST'])
@login_required(roles='mesero')
def enviar_orden_a_cocina(orden_id):
    orden = Orden.query.get_or_404(orden_id)
    if not orden.detalles:
        flash('No se puede enviar una orden vacía a cocina.', 'warning')
        return redirect(url_for('meseros.detalle_orden', orden_id=orden_id))
        
    if orden.estado != 'pendiente':
        flash(f'La orden #{orden.id} ya fue enviada o procesada ({orden.estado}).', 'warning')
    else:
        orden.estado = 'enviado' # Estado que indica que está en cocina
        # Todos los detalles de esta orden también deberían pasar a 'pendiente' (ya es su default)
        # o si tuvieran otro estado previo, actualizarlos.
        # for detalle in orden.detalles:
        #     if detalle.estado != 'pendiente': # O el estado inicial que quieras para cocina
        #         detalle.estado = 'pendiente'
        db.session.commit()
        flash('Orden enviada a cocina correctamente.', 'success')
        socketio.emit('nueva_orden_cocina', {'orden_id': orden.id, 'mensaje': f'Nueva orden #{orden.id} para cocina.'})
    # Redirigir al dashboard de meseros para ver el estado de la orden
    return redirect(url_for('meseros.view_meseros'))


@meseros_bp.route('/entregar_item/<int:orden_id>/<int:detalle_id>', methods=['POST'])
@login_required(roles=['mesero', 'admin', 'superadmin'])
def entregar_item(orden_id, detalle_id):
    detalle = OrdenDetalle.query.filter_by(id=detalle_id, orden_id=orden_id).first_or_404()
    
    if detalle.estado == 'entregado':
        return jsonify({"success": False, "message": "Este ítem ya fue entregado."}), 400
    if detalle.estado != 'listo': # Solo se pueden entregar ítems que están listos de cocina
        return jsonify({"success": False, "message": "Este ítem no está listo para entregar desde cocina."}), 400

    detalle.estado = 'entregado'
    # No es necesario un commit aquí si lo haces después de verificar la orden completa

    orden = Orden.query.options(joinedload(Orden.detalles)).get_or_404(orden_id)
    todos_detalles_entregados = all(d.estado == 'entregado' for d in orden.detalles)

    if todos_detalles_entregados:
        if orden.estado not in ['pagada', 'finalizada', 'cancelada', 'completada']:
            orden.estado = 'completada' 
            # Emitir evento de que la orden está lista para cobro (completamente entregada)
            socketio.emit('orden_actualizada_para_cobro', { # Renombré el evento
                'orden_id': orden.id, 
                'estado_orden': orden.estado,
                'mensaje': f'Orden #{orden.id} completamente entregada y lista para cobro.'
            })
    
    db.session.commit() # Un solo commit al final
    return jsonify(success=True, message="Ítem marcado como entregado.")


@meseros_bp.route('/ordenes/<int:orden_id>/cobrar_info', methods=['GET'])
@login_required(roles='mesero')
def get_cobrar_orden_info(orden_id): # Renombré para claridad vs la ruta POST
    orden = Orden.query.options(
        joinedload(Orden.mesa), # Para orden.mesa.numero
        joinedload(Orden.detalles).joinedload(OrdenDetalle.producto)
    ).get_or_404(orden_id)
    
    detalles_data = []
    for d in orden.detalles:
        detalles_data.append({
            "id": d.id,
            "nombre": d.producto.nombre,
            "cantidad": d.cantidad,
            "precio": d.producto.precio,
            "subtotal": d.producto.precio * d.cantidad,
            "estado": d.estado # MUY IMPORTANTE para el modal de cobro
        })
    total_calculado = sum(item["subtotal"] for item in detalles_data)
    
    return jsonify({
        "orden_id": orden.id, 
        "mesa_numero": orden.mesa.numero if orden.mesa else None,
        "es_para_llevar": orden.es_para_llevar,
        "estado_orden": orden.estado,
        "detalles": detalles_data, 
        "total": total_calculado
    })

@meseros_bp.route('/ordenes/<int:orden_id>/cobrar', methods=['POST'])
@login_required(roles='mesero')
def cobrar_orden_post(orden_id): # Renombré para claridad vs la ruta GET de info
    orden = Orden.query.options(joinedload(Orden.detalles).joinedload(OrdenDetalle.producto)).get_or_404(orden_id)
    
    print(f"[COBRAR_ORDEN] Iniciando cobro para orden #{orden_id}. Estado actual: {orden.estado}")
    print(f"[COBRAR_ORDEN] Request JSON: {request.json}")

    if orden.estado != 'completada':
        msg = f"La orden no está lista para cobro. Estado actual: {orden.estado} (se esperaba 'completada')."
        print(f"[COBRAR_ORDEN_ERROR] {msg}")
        return jsonify({"success": False, "message": msg}), 400

    # Verificar que todos los detalles estén realmente entregados (doble chequeo)
    detalles_no_entregados = [d for d in orden.detalles if d.estado != 'entregado']
    if detalles_no_entregados:
        nombres_pendientes = [d.producto.nombre for d in detalles_no_entregados]
        msg = f"No se puede cobrar. Ítems pendientes de entrega: {', '.join(nombres_pendientes)}."
        print(f"[COBRAR_ORDEN_ERROR] {msg}")
        return jsonify({"success": False, "message": msg}), 400

    data = request.get_json()
    if not data or 'monto_recibido' not in data:
        print(f"[COBRAR_ORDEN_ERROR] Datos de monto_recibido faltantes.")
        return jsonify({"success": False, "message": "Falta el monto recibido."}), 400

    try:
        monto_recibido_float = float(data['monto_recibido'])
    except ValueError:
        print(f"[COBRAR_ORDEN_ERROR] Monto recibido no es un número válido: {data['monto_recibido']}")
        return jsonify({"success": False, "message": "Monto recibido inválido."}), 400

    total_orden_calculado = sum(d.cantidad * d.producto.precio for d in orden.detalles)
    print(f"[COBRAR_ORDEN] Total calculado: {total_orden_calculado}, Monto recibido: {monto_recibido_float}")

    if monto_recibido_float < total_orden_calculado:
        msg = f"El monto recibido (${monto_recibido_float}) es menor al total de la orden (${total_orden_calculado})."
        print(f"[COBRAR_ORDEN_ERROR] {msg}")
        return jsonify({"success": False, "message": msg, "total_orden": total_orden_calculado}), 400

    # Actualizar orden
    orden.monto_recibido = monto_recibido_float
    orden.cambio = monto_recibido_float - total_orden_calculado
    orden.fecha_pago = datetime.utcnow()
    orden.estado = 'pagada' # Estado final

    # Crear registro de Venta (Sale)
    nueva_venta = Sale(
        mesa_id=orden.mesa_id,
        usuario_id=session.get('user_id'), # El mesero que cobró
        total=total_orden_calculado,
        estado='cerrada' # O el estado que uses para venta concretada
    )
    db.session.add(nueva_venta)
    db.session.flush() # Para obtener nueva_venta.id para los SaleItem

    for detalle_orden in orden.detalles:
        item_venta = SaleItem(
            sale_id=nueva_venta.id,
            producto_id=detalle_orden.producto_id,
            cantidad=detalle_orden.cantidad,
            precio_unitario=detalle_orden.producto.precio, # Tomar precio del producto al momento de la venta
            subtotal=detalle_orden.cantidad * detalle_orden.producto.precio
        )
        db.session.add(item_venta)
    
    db.session.commit()
    print(f"[COBRAR_ORDEN] Orden #{orden_id} pagada exitosamente. Cambio: ${orden.cambio}")
    
    # Emitir evento de que la orden fue pagada
    socketio.emit('orden_pagada_notificacion', {
        'orden_id': orden.id,
        'mensaje': f'Orden #{orden.id} ha sido pagada.'
    })

    return jsonify({
        "success": True, 
        "message": "Pago confirmado exitosamente.", 
        "cambio": orden.cambio,
        "orden_id": orden.id
    })

# Rutas que tenías para marcar entregado con booleano (considera eliminarlas o refactorizarlas)
# Si decides mantenerlas, asegúrate de que actualicen `detalle.estado` también para consistencia.
@meseros_bp.route('/ordenes/<int:orden_id>/producto/<int:detalle_id>/marcar_entregado_old', methods=['POST'])
@login_required(roles='mesero')
def marcar_producto_entregado_old(orden_id, detalle_id): # Renombrada para evitar conflicto
    detalle = OrdenDetalle.query.get_or_404(detalle_id)
    if detalle.orden_id != orden_id:
         return jsonify({"success": False, "message": "Detalle no pertenece a la orden."}), 400
    detalle.entregado = True # Usando el campo booleano
    # ¡Deberías también cambiar detalle.estado a 'entregado' aquí por consistencia!
    # detalle.estado = 'entregado' 
    db.session.commit()
    # Considera qué evento emitir. 'order_updated' es genérico.
    socketio.emit('order_updated', {'orden_id': orden_id, 'detalle_id': detalle_id, 'nuevo_estado_entregado_booleano': True})
    return jsonify({"success": True, "message": f"Producto {detalle.producto.nombre} marcado como entregado (booleano)."})

# ... (otras rutas como cancelar_orden, finalizar_orden (revisa su utilidad ahora), detalles_json, etc.)
# ... (el endpoint total_ordenes_activas es útil)