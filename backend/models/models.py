from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from backend.extensions import db

# -------------------- MODELOS --------------------

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), nullable=False)  # mesero, taquero, comal, admin
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

class Estacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    productos = db.relationship('Producto', backref='estacion', lazy=True)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(50))
    descripcion = db.Column(db.Text)

    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    categoria = db.relationship('Categoria', backref='productos')

    estacion_id = db.Column(db.Integer, db.ForeignKey('estacion.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'unidad': self.unidad,
            'descripcion': self.descripcion,
            'categoria': self.categoria.nombre if self.categoria else None,
            'estacion': self.estacion.nombre if self.estacion else None
        }

class Mesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), nullable=False, unique=True)
    ordenes = db.relationship('Orden', backref='mesa', lazy=True)

class Orden(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey('mesa.id'))
    mesero_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    estado = db.Column(db.String(50), default='pendiente')  # pendiente, en_preparacion, lista, entregada
    es_para_llevar = db.Column(db.Boolean, default=False)
    tiempo_registro = db.Column(db.DateTime, default=datetime.utcnow)

    mesero = db.relationship('Usuario', backref='ordenes')
    detalles = db.relationship('OrdenDetalle', backref='orden', lazy=True)
    productos = db.relationship('Producto', secondary='orden_detalle', viewonly=True, backref='ordenes')

    def to_dict(self):
        return {
            'id': self.id,
            'mesa_id': self.mesa_id,
            'mesero_id': self.mesero_id,
            'estado': self.estado,
            'es_para_llevar': self.es_para_llevar,
            'tiempo_registro': self.tiempo_registro.isoformat(),
            'detalles': [detalle.to_dict() for detalle in self.detalles]
        }

class OrdenDetalle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    cantidad = db.Column(db.Integer, default=1)
    notas = db.Column(db.String(200))
    estado      = db.Column(db.String(20), nullable=False, default='pendiente') 
    entregado = db.Column(db.Boolean, default=False)
    
    producto = db.relationship('Producto', backref='orden_detalles')

    def to_dict(self):
        return {
            'id': self.id,
            'orden_id': self.orden_id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'notas': self.notas,
            'producto': self.producto.to_dict(),
            'entregado': self.entregado
        }