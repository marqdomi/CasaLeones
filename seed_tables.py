# seed_tables.py
from app import create_app
from models.database import db
from models.models import Mesa

def seed_tables():
    for numero in range(1, 9):
        mesa_existente = Mesa.query.filter_by(numero=numero).first()
        if not mesa_existente:
            nueva_mesa = Mesa(numero=numero)
            db.session.add(nueva_mesa)
    db.session.commit()
    print("Mesas sembradas correctamente.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_tables()