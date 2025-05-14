from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from backend.models.models import Orden, OrdenDetalle, Producto
from backend.extensions import db, socketio

def verificar_orden_completa(orden_id):
    """
    Marca la orden como 'lista_para_entregar' si todos sus detalles están en estado 'listo'.
    """
    detalles = OrdenDetalle.query.filter_by(orden_id=orden_id).all()
    try:
        if detalles and all(d.estado == 'listo' for d in detalles):
            orden = Orden.query.get(orden_id)
            # Solo cambiar si no está ya en un estado final
            if orden.estado not in ['finalizada', 'pagada', 'lista_para_entregar']:
                orden.estado = 'lista_para_entregar'
                db.session.commit()  # COMMIT inmediato
                socketio.emit('orden_completa_lista', {
                    'orden_id': orden.id,
                    'mesa_nombre': orden.mesa.numero if orden.mesa else 'Para Llevar',
                    'mensaje': f'¡Toda la orden {orden.id} está lista para entregar!'
                })
            return True
    except AttributeError:
        # Si OrdenDetalle no tiene atributo 'estado', omitimos el chequeo.
        return False
    return False

def login_required(roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Si no hay sesión iniciada:
            if 'user_id' not in session:
                # Responder JSON para llamadas AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Debes iniciar sesión'}), 401
                # Mantener comportamiento anterior para navegadores
                flash('Debes iniciar sesión', 'warning')
                return redirect(url_for('auth.login'))
            # Si hay roles y no coincide (permitir siempre a superadmin):
            if roles:
                allowed = roles if isinstance(roles, (list, tuple)) else [roles]
                user_role = session.get('rol')
                if user_role != 'superadmin' and user_role not in allowed:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'error': 'No tienes permiso'}), 403
                    flash('No tienes permiso para acceder a esta página', 'danger')
                    # Redirect based on the user's actual role
                    if user_role == 'mesero':
                        return redirect(url_for('meseros.view_meseros'))
                    elif user_role in ('cocinero', 'comal', 'taqueros', 'bebidas'):
                        return redirect(url_for('cocina.view_cocina'))
                    return redirect(url_for('auth.login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

def obtener_ordenes_por_estacion(estacion):
    """
    Devuelve un diccionario que mapea cada orden_id a la lista de
    OrdenDetalle pendientes para la estación indicada.
    """
    detalles = (
        OrdenDetalle.query
        .filter(
            OrdenDetalle.estado != 'listo',
            OrdenDetalle.producto.has(estacion=estacion)
        )
        .all()
    )
    ordenes_por_estacion = {}
    for d in detalles:
        ordenes_por_estacion.setdefault(d.orden_id, []).append(d)
    return ordenes_por_estacion