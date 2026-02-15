# backend/models/database.py

import logging
from backend.extensions import db

logger = logging.getLogger(__name__)


def init_db():
    """Create all tables if they don't exist."""
    import backend.models.models  # noqa: F401
    db.create_all()
    logger.info('Base de datos inicializada correctamente.')
