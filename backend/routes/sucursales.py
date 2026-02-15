"""Fase 4 — Item 23: Multi-sucursal — CRUD y selección de sucursal."""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from backend.utils import login_required
from backend.extensions import db
from backend.models.models import Sucursal, Usuario
from flask_login import current_user

logger = logging.getLogger(__name__)

sucursales_bp = Blueprint('sucursales', __name__, url_prefix='/admin/sucursales')


@sucursales_bp.route('/')
@login_required(roles=['superadmin'])
def lista_sucursales():
    sucursales = Sucursal.query.order_by(Sucursal.nombre).all()
    return render_template('admin/sucursales/lista.html', sucursales=sucursales)


@sucursales_bp.route('/nueva', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def nueva_sucursal():
    if request.method == 'POST':
        s = Sucursal(
            nombre=request.form['nombre'],
            direccion=request.form.get('direccion', ''),
            telefono=request.form.get('telefono', ''),
        )
        db.session.add(s)
        db.session.commit()
        flash('Sucursal creada.', 'success')
        return redirect(url_for('sucursales.lista_sucursales'))
    return render_template('admin/sucursales/form.html')


@sucursales_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required(roles=['superadmin'])
def editar_sucursal(id):
    s = Sucursal.query.get_or_404(id)
    if request.method == 'POST':
        s.nombre = request.form['nombre']
        s.direccion = request.form.get('direccion', '')
        s.telefono = request.form.get('telefono', '')
        s.activa = 'activa' in request.form
        db.session.commit()
        flash('Sucursal actualizada.', 'success')
        return redirect(url_for('sucursales.lista_sucursales'))
    return render_template('admin/sucursales/form.html', sucursal=s)


@sucursales_bp.route('/seleccionar/<int:id>', methods=['POST'])
@login_required(roles=['superadmin', 'admin', 'mesero'])
def seleccionar_sucursal(id):
    """Guarda la sucursal activa en sesión."""
    s = Sucursal.query.get_or_404(id)
    session['sucursal_id'] = s.id
    session['sucursal_nombre'] = s.nombre
    flash(f'Sucursal: {s.nombre}', 'info')
    return redirect(request.referrer or url_for('meseros.view_meseros'))


@sucursales_bp.route('/api/lista')
@login_required(roles=['superadmin', 'admin'])
def api_lista():
    sucursales = Sucursal.query.filter_by(activa=True).order_by(Sucursal.nombre).all()
    return jsonify([{'id': s.id, 'nombre': s.nombre} for s in sucursales])
