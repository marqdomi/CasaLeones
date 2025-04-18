# backend/models/database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    # Import model modules so they are registered with SQLAlchemy
    import backend.models.models  # noqa: F401
    db.create_all()