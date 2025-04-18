from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

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

class OrdenDetalle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    cantidad = db.Column(db.Integer, default=1)
    notas = db.Column(db.String(200))

    producto = db.relationship('Producto', backref='orden_detalles')