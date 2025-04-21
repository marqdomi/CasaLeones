from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user
from backend.models.models import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(password):
            login_user(usuario)
            session['user_id'] = usuario.id
            session['email'] = usuario.email
            session['rol'] = usuario.rol
            flash('Inicio de sesión exitoso', 'success')
            # Redirigir a dashboard según rol
            if usuario.rol == 'mesero':
                return redirect(url_for('meseros.view_meseros'))
            elif usuario.rol == 'taquero':
                return redirect(url_for('cocina.view_taqueros'))
            elif usuario.rol == 'comal':
                return redirect(url_for('cocina.view_comal'))
            elif usuario.rol == 'bebidas':
                return redirect(url_for('cocina.view_bebidas'))
            elif usuario.rol == 'admin':
                return redirect(url_for('admin.crear_usuario'))
            else:
                flash('Rol desconocido', 'danger')
                return redirect(url_for('auth.login'))
        else:
            flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('auth.login'))