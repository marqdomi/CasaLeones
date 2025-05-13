# backend/models/database.py

from backend.extensions import db

def init_db():
    # Importar los modelos para que db conozca todas las tablas
    import backend.models.models  # noqa: F401
    db.create_all()
    # Agregar columna usuario_id a corte_caja si no existe
    engine = db.get_engine()
    try:
        engine.execute('ALTER TABLE corte_caja ADD COLUMN usuario_id INTEGER')
    except Exception:
        pass