#!/usr/bin/env python3
from backend.app import create_app
from backend.extensions import db
from backend.models.models import Mesa

def seed_mesas():
    app = create_app()
    with app.app_context():
        # Eliminar mesas existentes (opcional)
        db.session.query(Mesa).delete()
        # Crear 8 mesas numeradas del 1 al 8
        for numero in range(1, 9):
            mesa = Mesa(numero=numero)
            db.session.add(mesa)
        db.session.commit()
        print("Se han sembrado las 8 mesas (1–8) con éxito.")

if __name__ == "__main__":
    seed_mesas()
