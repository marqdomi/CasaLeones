

from backend.extensions import db, Producto, Estacion
from backend.app import create_app

app = create_app()

# Diccionario de mapeo de categorías a estaciones
mapeo_estaciones = {
    "Tacos": "taquero",
    "Quesadillas": "comal",
    "Platos Fuertes": "taquero",
    "Consomé": "taquero",
    "Bebidas": "bebidas"
}

with app.app_context():
    estaciones = {e.nombre.lower(): e for e in Estacion.query.all()}
    productos = Producto.query.all()
    cambios = 0

    for producto in productos:
        if producto.categoria in mapeo_estaciones:
            nombre_estacion = mapeo_estaciones[producto.categoria]
            estacion = estaciones.get(nombre_estacion)
            if estacion:
                producto.estacion = estacion
                cambios += 1

    db.session.commit()
    print(f"Se actualizaron {cambios} productos con su estación correspondiente.")