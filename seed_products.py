from app import create_app
from models.database import db
from models.models import Categoria, Producto, Estacion

def seed_menu():
    # Definir las categorías del menú
    categorias_data = [
        {"nombre": "Tacos de Barbacoa"},
        {"nombre": "Tacos de Carnitas"},
        {"nombre": "Tacos de Pollo"},
        {"nombre": "Quesadillas"},
        {"nombre": "Tlacoyos"},
        {"nombre": "Porciones de Barbacoa"},
        {"nombre": "Porciones de Carnitas"},
        {"nombre": "Mixiote"},
        {"nombre": "Antojitos"},
        {"nombre": "Consomé"},
        {"nombre": "Paquetes"},
        {"nombre": "Bebidas"}
    ]

    for cat in categorias_data:
        categoria = Categoria.query.filter_by(nombre=cat["nombre"]).first()
        if not categoria:
            categoria = Categoria(nombre=cat["nombre"])
            db.session.add(categoria)
    db.session.commit()

    # Crear un diccionario para facilitar la referencia de las categorías
    categorias = { c.nombre: c for c in Categoria.query.all() }

    # Agregar si no existen las estaciones necesarias
    estaciones_data = ["comal", "taquero", "bebidas"]
    for nombre in estaciones_data:
        estacion = Estacion.query.filter_by(nombre=nombre).first()
        if not estacion:
            db.session.add(Estacion(nombre=nombre))
    db.session.commit()

    # Crear un diccionario para mapear nombres de estaciones a sus IDs
    estaciones = { e.nombre: e for e in Estacion.query.all() }
    
    taquero = estaciones.get("taquero")
    comal = estaciones.get("comal")
    bebidas = estaciones.get("bebidas")

    # Lista de productos de ejemplo
    products_data = [
        # Tacos de Barbacoa
        {"nombre": "Espaldilla", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Falda", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Costilla", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Maciza", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Panza", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Cabeza", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Ojo", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Lengua", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Cachete", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Pezcueso", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Espinazo (surtida)", "precio": 35.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Campechano maciza con panza", "precio": 38.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Campechano espaldilla con panza", "precio": 38.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Campechano falda con panza", "precio": 38.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Campechano costilla con panza", "precio": 38.0, "categoria": "Tacos de Barbacoa", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        # Tacos de Carnitas
        {"nombre": "Maciza", "precio": 35.0, "categoria": "Tacos de Carnitas", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Costilla", "precio": 35.0, "categoria": "Tacos de Carnitas", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Tripa", "precio": 35.0, "categoria": "Tacos de Carnitas", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Cuerito", "precio": 35.0, "categoria": "Tacos de Carnitas", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        # Tacos de Pollo
        {"nombre": "Taco de pollo", "precio": 35.0, "categoria": "Tacos de Pollo", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        # Quesadillas
        {"nombre": "Chicharrón prensado", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Champiñón", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Queso", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Huitlacoche", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Mole verde", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Jamón con queso", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Flor de calabaza", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Tinga", "precio": 33.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Barbacoa", "precio": 65.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Carnitas", "precio": 40.0, "categoria": "Quesadillas", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        # Tlacoyos
        {"nombre": "Frijol", "precio": 33.0, "categoria": "Tlacoyos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Requesón", "precio": 33.0, "categoria": "Tlacoyos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Alberjón", "precio": 33.0, "categoria": "Tlacoyos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Chicharrón prensado", "precio": 33.0, "categoria": "Tlacoyos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Barbacoa", "precio": 33.0, "categoria": "Tlacoyos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Carnitas", "precio": 33.0, "categoria": "Tlacoyos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        # Porciones de Barbacoa
        {"nombre": "1 kg Barbacoa", "precio": 550.0, "categoria": "Porciones de Barbacoa", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        {"nombre": "3/4 kg Barbacoa", "precio": 415.0, "categoria": "Porciones de Barbacoa", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        {"nombre": "1/2 kg Barbacoa", "precio": 280.0, "categoria": "Porciones de Barbacoa", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        {"nombre": "1/4 kg Barbacoa", "precio": 140.0, "categoria": "Porciones de Barbacoa", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        # Porciones de Carnitas
        {"nombre": "1 kg Carnitas", "precio": 300.0, "categoria": "Porciones de Carnitas", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        {"nombre": "3/4 kg Carnitas", "precio": 225.0, "categoria": "Porciones de Carnitas", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        {"nombre": "1/2 kg Carnitas", "precio": 150.0, "categoria": "Porciones de Carnitas", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        {"nombre": "1/4 kg Carnitas", "precio": 80.0, "categoria": "Porciones de Carnitas", "estacion_id": "taquero", "unidad": "kg", "descripcion": ""},
        # Mixiote
        {"nombre": "Mixiote de Pollo (1 para llevar)", "precio": 80.0, "categoria": "Mixiote", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Mixiote de Pollo (1 para comer aquí)", "precio": 90.0, "categoria": "Mixiote", "estacion_id": "taquero", "unidad": "pieza", "descripcion": ""},
        # Antojitos
        {"nombre": "Orden de tacos dorados (3 flautas)", "precio": 90.0, "categoria": "Antojitos", "estacion_id": "comal", "unidad": "orden", "descripcion": ""},
        {"nombre": "1 flauta individual", "precio": 33.0, "categoria": "Antojitos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        {"nombre": "1 kg Tortillas", "precio": 30.0, "categoria": "Antojitos", "estacion_id": "comal", "unidad": "pieza", "descripcion": ""},
        # Consomé
        {"nombre": "Plato de consomé", "precio": 35.0, "categoria": "Consomé", "estacion_id": "taquero", "unidad": "plato", "descripcion": ""},
        {"nombre": "1 litro de consomé", "precio": 60.0, "categoria": "Consomé", "estacion_id": "taquero", "unidad": "litro", "descripcion": ""},
        {"nombre": "1/2 litro de consomé", "precio": 35.0, "categoria": "Consomé", "estacion_id": "taquero", "unidad": "litro", "descripcion": ""},
        # Paquetes para llevar
        {"nombre": "1/4 kg barbacoa + 1 plato consomé", "precio": 175.0, "categoria": "Paquetes", "estacion_id": "taquero", "unidad": "paquete", "descripcion": ""},
        {"nombre": "1/2 kg barbacoa + 1 lt consomé", "precio": 340.0, "categoria": "Paquetes", "estacion_id": "taquero", "unidad": "paquete", "descripcion": ""},
        {"nombre": "3/4 kg barbacoa + 1 1/2 lt consomé", "precio": 500.0, "categoria": "Paquetes", "estacion_id": "taquero", "unidad": "paquete", "descripcion": ""},
        {"nombre": "1 kg barbacoa + 2 lt consomé", "precio": 670.0, "categoria": "Paquetes", "estacion_id": "taquero", "unidad": "paquete", "descripcion": ""},
        {"nombre": "Mixiote de Pollo (1 para llevar)", "precio": 90.0, "categoria": "Paquetes", "estacion_id": "taquero", "unidad": "paquete", "descripcion": ""},
        # Bebidas
        {"nombre": "Coca-Cola", "precio": 25.0, "categoria": "Bebidas", "estacion_id": "bebidas", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Boing", "precio": 25.0, "categoria": "Bebidas", "estacion_id": "bebidas", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Agua Jamaica", "precio": 40.0, "categoria": "Bebidas", "estacion_id": "bebidas", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Agua sabor", "precio": 45.0, "categoria": "Bebidas", "estacion_id": "bebidas", "unidad": "pieza", "descripcion": ""},
        {"nombre": "Café", "precio": 25.0, "categoria": "Bebidas", "estacion_id": "bebidas", "unidad": "pieza", "descripcion": ""}
    ]
    
    for prod in products_data:
        producto = Producto.query.filter_by(nombre=prod["nombre"]).first()
        estacion = estaciones.get(prod.get("estacion_id"))
        if not producto:
            producto = Producto(
                nombre=prod["nombre"],
                precio=prod["precio"],
                categoria_id=categorias[prod["categoria"]].id,
                estacion_id=estacion.id if estacion else None,
                unidad=prod.get("unidad"),
                descripcion=prod.get("descripcion")
            )
            db.session.add(producto)
        else:
            producto.estacion_id = estacion.id if estacion else None
            producto.categoria_id = categorias[prod["categoria"]].id
            db.session.add(producto)
    print(f"Asignando estación a {prod['nombre']}: {estacion.nombre if estacion else 'Ninguna'}")        
    db.session.commit()
    print("Productos y categorías sembrados correctamente.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Ejecuta solo la siembra, sin eliminar ni recrear las tablas
        seed_menu()
    print("Base de datos poblada con éxito.")