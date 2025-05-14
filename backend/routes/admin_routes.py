from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from backend.utils import login_required
from backend.extensions import db
from backend.models.models import Sale, SaleItem, Producto, Mesa, CorteCaja, Usuario, Categoria, Estacion
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash
from flask import current_app
from datetime import date
from flask_login import current_user

#print("Cargando admin_routes.py...")

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@login_required(roles=['admin','superadmin'])
def dashboard():
    """Admin dashboard landing page."""
    return render_template('admin/dashboard.html')

@admin_bp.route('/crear_usuario', methods=['GET', 'POST'])
@login_required(roles=['admin','superadmin'])
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
        return redirect(url_for('admin.lista_usuarios'))

    return render_template('admin/usuario_form.html')

@admin_bp.route('/api/dashboard/ventas_hoy')
@login_required(roles=['admin','superadmin'])
def api_ventas_hoy():
    hoy = date.today()
    total = db.session.query(db.func.sum(Sale.total)) \
        .filter(db.func.date(Sale.fecha_hora) == hoy).scalar() or 0
    return jsonify({'ventasHoy': float(total)})

@admin_bp.route('/api/dashboard/ordenes_hoy')
@login_required(roles=['admin','superadmin'])
def api_ordenes_hoy():
    hoy = date.today()
    count = Sale.query.filter(db.func.date(Sale.fecha_hora) == hoy).count()
    return jsonify({'ordenesHoy': count})

@admin_bp.route('/api/dashboard/ticket_promedio')
@login_required(roles=['admin','superadmin'])
def api_ticket_promedio():
    hoy = date.today()
    ventas = Sale.query.filter(db.func.date(Sale.fecha_hora) == hoy).all()
    if not ventas:
        return jsonify({'ticketPromedio': 0})
    promedio = sum(v.total for v in ventas) / len(ventas)
    return jsonify({'ticketPromedio': float(promedio)})

@admin_bp.route('/api/dashboard/top_productos')
@login_required(roles=['admin','superadmin'])
def api_top_productos():
    hoy = date.today()
    results = db.session.query(
        Producto.nombre,
        db.func.sum(SaleItem.cantidad).label('cantidad')
    ).join(SaleItem, SaleItem.producto_id == Producto.id) \
     .join(Sale, SaleItem.sale_id == Sale.id) \
     .filter(db.func.date(Sale.fecha_hora) == hoy) \
     .group_by(Producto.id) \
     .order_by(db.desc('cantidad')) \
     .limit(5) \
     .all()
    return jsonify({
        'labels': [r[0] for r in results],
        'data':   [int(r[1]) for r in results]
    })

# --- Usuarios CRUD ---
@admin_bp.route('/usuarios')
@login_required(roles=['superadmin'])
def lista_usuarios():
    usuarios = Usuario.query.order_by(Usuario.rol, Usuario.nombre).all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def usuario_nuevo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        rol = request.form['rol']
        password = request.form['password']
        if Usuario.query.filter_by(email=email).first():
            flash('Email ya existe', 'danger')
            return redirect(url_for('admin.usuario_nuevo'))
        u = Usuario(nombre=nombre, email=email, rol=rol)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash('Usuario creado', 'success')
        return redirect(url_for('admin.lista_usuarios'))
    return render_template('admin/usuario_form.html')

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def usuario_editar(id):
    u = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        u.nombre = request.form['nombre']
        u.email = request.form['email']
        u.rol = request.form['rol']
        db.session.commit()
        flash('Usuario actualizado', 'success')
        return redirect(url_for('admin.lista_usuarios'))
    return render_template('admin/usuario_form.html', usuario=u)

@admin_bp.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required(roles=['superadmin'])
def usuario_eliminar(id):
    u = Usuario.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    flash('Usuario eliminado', 'success')
    return redirect(url_for('admin.lista_usuarios'))


# --- Productos CRUD ---
@admin_bp.route('/productos')
@login_required(roles=['superadmin'])
def lista_productos():
    productos = Producto.query.options(
        joinedload(Producto.categoria),
        joinedload(Producto.estacion)
    ).order_by(Producto.nombre).all()
    return render_template('admin/productos.html', productos=productos)

@admin_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def producto_nuevo():
    if request.method == 'POST':
        p = Producto(
            nombre=request.form['nombre'],
            precio=float(request.form['precio']),
            unidad=request.form.get('unidad'),
            descripcion=request.form.get('descripcion'),
            categoria_id=int(request.form['categoria_id']),
            estacion_id=int(request.form['estacion_id'])
        )
        db.session.add(p)
        db.session.commit()
        flash('Producto creado', 'success')
        return redirect(url_for('admin.lista_productos'))
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    estaciones = Estacion.query.order_by(Estacion.nombre).all()
    return render_template(
        'admin/producto_form.html',
        categorias=categorias,
        estaciones=estaciones
    )

@admin_bp.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def producto_editar(id):
    p = Producto.query.get_or_404(id)
    if request.method == 'POST':
        p.nombre = request.form['nombre']
        p.precio = float(request.form['precio'])
        p.unidad = request.form.get('unidad')
        p.descripcion = request.form.get('descripcion')
        p.categoria_id = int(request.form['categoria_id'])
        p.estacion_id = int(request.form['estacion_id'])
        db.session.commit()
        flash('Producto actualizado', 'success')
        return redirect(url_for('admin.lista_productos'))
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    estaciones = Estacion.query.order_by(Estacion.nombre).all()
    return render_template(
        'admin/producto_form.html',
        producto=p,
        categorias=categorias,
        estaciones=estaciones
    )

@admin_bp.route('/productos/<int:id>/eliminar', methods=['POST'])
@login_required(roles=['superadmin'])
def producto_eliminar(id):
    p = Producto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Producto eliminado', 'success')
    return redirect(url_for('admin.lista_productos'))


# --- Mesas CRUD ---
@admin_bp.route('/mesas')
@login_required(roles=['superadmin'])
def lista_mesas():
    mesas = Mesa.query.order_by(Mesa.numero).all()
    return render_template('admin/mesas.html', mesas=mesas)

@admin_bp.route('/mesas/nuevo', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def mesa_nuevo():
    if request.method == 'POST':
        m = Mesa(numero=request.form['numero'])
        db.session.add(m)
        db.session.commit()
        flash('Mesa creada', 'success')
        return redirect(url_for('admin.lista_mesas'))
    return render_template('admin/mesa_form.html')

@admin_bp.route('/mesas/<int:id>/editar', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def mesa_editar(id):
    m = Mesa.query.get_or_404(id)
    if request.method == 'POST':
        m.numero = request.form['numero']
        db.session.commit()
        flash('Mesa actualizada', 'success')
        return redirect(url_for('admin.lista_mesas'))
    return render_template('admin/mesa_form.html', mesa=m)

@admin_bp.route('/mesas/<int:id>/eliminar', methods=['POST'])
@login_required(roles=['superadmin'])
def mesa_eliminar(id):
    m = Mesa.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash('Mesa eliminada', 'success')
    return redirect(url_for('admin.lista_mesas'))


# --- Corte de Caja ---
@admin_bp.route('/corte-caja', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def corte_caja():
    resumen = {}
    hoy = date.today()
    # calcular totales de hoy
    total = db.session.query(db.func.sum(Sale.total)).filter(db.func.date(Sale.fecha_hora) == hoy).scalar() or 0
    count = Sale.query.filter(db.func.date(Sale.fecha_hora) == hoy).count()
    promedio = (total / count) if count else 0
    resumen.update({
        'fecha': hoy,
        'total_ingresos': float(total),
        'num_ordenes': count,
        'ticket_promedio': float(promedio)
    })
    if request.method == 'POST':
        corte = CorteCaja(
            fecha=hoy,
            total_ingresos=resumen['total_ingresos'],
            num_ordenes=resumen['num_ordenes'],
            usuario_id=current_user.id
        )
        db.session.add(corte)
        db.session.commit()
        flash('Corte de caja generado', 'success')
        return redirect(url_for('admin.corte_caja'))
    cortes = CorteCaja.query\
        .options(joinedload(CorteCaja.usuario))\
        .order_by(CorteCaja.fecha.desc())\
        .all()
    return render_template('admin/corte_caja.html', resumen=resumen, cortes=cortes)

from backend.routes.meseros import meseros_bp
admin_bp.register_blueprint(meseros_bp, url_prefix="/meseros")
