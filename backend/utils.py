from functools import wraps
from flask import session, redirect, url_for, flash
from backend.models.models import Orden, OrdenDetalle, Producto
from backend.extensions import db

def verificar_orden_completa(orden_id):
    """
    Marca la orden como 'lista' si todos sus detalles están en estado 'listo'.
    """
    detalles = OrdenDetalle.query.filter_by(orden_id=orden_id).all()
    try:
        if detalles and all(d.estado == 'listo' for d in detalles):
            orden = Orden.query.get(orden_id)
            orden.estado = 'lista'
            db.session.commit()
            return True
    except AttributeError:
        # Si OrdenDetalle no tiene atributo 'estado', omitimos el chequeo.
        return False
    return False

def login_required(rol=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            # Si no hay sesión iniciada:
            if 'user_id' not in session:
                if request.blueprint == 'api':
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Debes iniciar sesión', 'warning')
                return redirect(url_for('auth.login'))
            # Si hay rol y no coincide:
            if rol and session.get('rol') != rol:
                if request.blueprint == 'api':
                    return jsonify({'error': 'Forbidden'}), 403
                flash('No tienes permiso para acceder a esta página', 'danger')
                if session.get('rol') == 'mesero':
                    return redirect(url_for('meseros.view_meseros'))
                return redirect(url_for('cocina.view_cocina'))
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