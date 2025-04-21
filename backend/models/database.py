# backend/models/database.py

from backend.extensions import db

def init_db():
    # Importar los modelos para que db conozca todas las tablas
    import backend.models.models  # noqa: F401
    db.create_all()