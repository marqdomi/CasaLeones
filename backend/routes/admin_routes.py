from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import db, Usuario
from werkzeug.security import generate_password_hash
from .decorators import rol_requerido
from routes.meseros import meseros_bp

print("Cargando admin_routes.py...")

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/crear_usuario', methods=['GET', 'POST'])
@login_required
@rol_requerido('admin')
def crear_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']

        if Usuario.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('admin.crear_usuario'))

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            rol=rol
        )
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('admin.crear_usuario'))

    return render_template('admin_crear_usuario.html')
