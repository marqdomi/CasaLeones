"""Rutas legacy de productos.

El CRUD vigente de productos vive en `admin_routes` (endpoints `admin.lista_productos`,
`admin.producto_nuevo`, `admin.producto_editar`, `admin.producto_eliminar`), que es el
que enlaza el sidebar. Este blueprint sólo conserva las URLs antiguas y redirige, para
que no existan dos pantallas de productos divergentes bajo el mismo prefijo.
"""
from flask import Blueprint, redirect, url_for

from backend.utils import login_required

productos_bp = Blueprint('productos', __name__, url_prefix='/admin/productos')


@productos_bp.route('/', methods=['GET'])
@login_required(roles=['admin', 'superadmin'])
def listar_productos():
    return redirect(url_for('admin.lista_productos'))


@productos_bp.route('/crear', methods=['GET', 'POST'])
@login_required(roles=['admin', 'superadmin'])
def crear_producto():
    return redirect(url_for('admin.producto_nuevo'))


@productos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required(roles=['admin', 'superadmin'])
def editar_producto(id):
    return redirect(url_for('admin.producto_editar', id=id))


@productos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required(roles=['superadmin'])
def eliminar_producto(id):
    return redirect(url_for('admin.lista_productos'))
