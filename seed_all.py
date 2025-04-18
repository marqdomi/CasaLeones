# seed_all.py
import csv
from app import create_app
from models.database import db
from models.models import Usuario, Mesa, Silla, Categoria, Producto, Estacion

def seed_users():
    # Ejemplo: 3 meseros, 1 taquero y 1 comal
    usuarios_data = [
        {'username': 'mesero1', 'password': 'password1', 'rol': 'mesero'},
        {'username': 'mesero2', 'password': 'password2', 'rol': 'mesero'},
        {'username': 'mesero3', 'password': 'password3', 'rol': 'mesero'},
        {'username': 'taquero1', 'password': 'password4', 'rol': 'taquero'},
        {'username': 'comal1', 'password': 'password5', 'rol': 'comal'},
    ]
    for data in usuarios_data:
        usuario = Usuario.query.filter_by(username=data['username']).first()
        if not usuario:
            usuario = Usuario(username=data['username'], rol=data['rol'])
            usuario.set_password(data['password'])
            db.session.add(usuario)
    db.session.commit()
    print("Usuarios creados.")

def seed_tables():
    # Datos: (nombre de la mesa, cantidad de sillas)
    tables_data = [
        ("Mesa 1", 4),
        ("Mesa 2", 6),
        ("Mesa 3", 6),
        ("Mesa 4", 8),
        ("Mesa 5", 10),
        ("Mesa 6", 10),
        ("Mesa 7", 10),
        ("Mesa 8", 12)
    ]
    for mesa_num, chairs in tables_data:
        mesa = Mesa.query.filter_by(numero=mesa_num).first()
        if not mesa:
            mesa = Mesa(numero=mesa_num)
            db.session.add(mesa)
            db.session.commit()  # Para obtener el ID de la mesa
        for i in range(1, chairs + 1):
            silla = Silla.query.filter_by(mesa_id=mesa.id, numero=i).first()
            if not silla:
                silla = Silla(numero=i, mesa_id=mesa.id)
                db.session.add(silla)
        db.session.commit()
    print("Mesas y sillas sembradas.")

def seed_products_from_csv():
    # Abrir el archivo CSV y procesarlo
    with open("menu_restaurante.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Obtener los valores de cada columna y limpiar espacios
            categoria_name = row.get("Categoria", "").strip()
            nombre = row.get("Nombre", "").strip()
            precio_str = row.get("Precio", "").strip()
            unidad = row.get("Unidad", "").strip() or None
            descripcion = row.get("Descripcion", "").strip() or None
            estacion_name = row.get("Estacion", "").strip()
            
            # Convertir el precio a float (si falla, usar 0.0)
            try:
                precio = float(precio_str)
            except ValueError:
                precio = 0.0
            
            # Obtener o crear la categoría
            categoria = Categoria.query.filter_by(nombre=categoria_name).first()
            if not categoria:
                categoria = Categoria(nombre=categoria_name)
                db.session.add(categoria)
                db.session.commit()
            
            # Obtener o crear la estación si se proporciona (por ejemplo, "Taquero" o "Comal")
            estacion = None
            if estacion_name:
                estacion = Estacion.query.filter_by(nombre=estacion_name).first()
                if not estacion:
                    # Si no existe, la creamos
                    estacion = Estacion(nombre=estacion_name)
                    db.session.add(estacion)
                    db.session.commit()
            
            # Verificar si ya existe el producto (por nombre)
            producto = Producto.query.filter_by(nombre=nombre).first()
            if not producto:
                producto = Producto(
                    nombre=nombre,
                    precio=precio,
                    categoria_id=categoria.id,
                    estacion_id=estacion.id if estacion else None,
                    unidad=unidad,
                    descripcion=descripcion
                )
                db.session.add(producto)
        db.session.commit()
    print("Productos y categorías sembrados desde CSV.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Opcional: eliminar todas las tablas para iniciar de cero
        db.drop_all()
        db.create_all()
        seed_users()
        seed_tables()
        seed_products_from_csv()
    print("Base de datos poblada con éxito.")