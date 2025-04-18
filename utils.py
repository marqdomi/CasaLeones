# utils.py
from functools import wraps
from flask import session, redirect, url_for, flash
from models.models import Orden, OrdenDetalle
from models.database import db

def verificar_orden_completa(orden_id):
    detalles = OrdenDetalle.query.filter_by(orden_id=orden_id).all()
    if detalles and all(d.estado == 'listo' for d in detalles):
        orden = Orden.query.get(orden_id)
        orden.estado = 'lista'
        db.session.commit()
        return True
    return False

def login_required(rol=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión', 'warning')
                return redirect(url_for('auth.login'))
            if rol and session.get('rol') != rol:
                flash('No tienes permiso para acceder a esta página', 'danger')
                # Redirigir a la página que corresponda según el rol
                if session.get('rol') == 'mesero':
                    return redirect(url_for('meseros.view_meseros'))
                else:
                    return redirect(url_for('cocina.view_cocina'))
            return func(*args, **kwargs)
        return wrapper
    return decorator