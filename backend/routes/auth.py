from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user
from backend.models.models import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Debug logs
        print(f"[DEBUG] login attempt: email={email}", flush=True)
        usuario = Usuario.query.filter_by(email=email).first()
        print(f"[DEBUG] user exists: {bool(usuario)}", flush=True)
        if usuario:
            print(f"[DEBUG] stored hash: {usuario.password_hash}", flush=True)
            valid = usuario.check_password(password)
            print(f"[DEBUG] password valid? {valid}", flush=True)
        else:
            valid = False

        if valid:
            login_user(usuario)
            session['user_id'] = usuario.id
            session['rol'] = usuario.rol
            flash('Inicio de sesión exitoso', 'success')
            # Redirect based on role
            if usuario.rol in ('superadmin', 'admin'):
                # Superadmin and admin go to user management
                return redirect(url_for('admin.crear_usuario'))
            elif usuario.rol == 'mesero':
                return redirect(url_for('meseros.view_meseros'))
            elif usuario.rol == 'taquero':
                return redirect(url_for('cocina.view_taqueros'))
            elif usuario.rol == 'comal':
                return redirect(url_for('cocina.view_comal'))
            elif usuario.rol == 'bebidas':
                return redirect(url_for('cocina.view_bebidas'))
            # Fallback to login if role unrecognized
            return redirect(url_for('auth.login'))
        else:
            flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('auth.login'))