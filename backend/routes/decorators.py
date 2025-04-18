from functools import wraps
from flask import session, redirect, url_for, flash

def rol_requerido(rol):
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            if 'rol' not in session or session['rol'] != rol:
                flash('Acceso no autorizado.', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return funcion_decorada
    return decorador