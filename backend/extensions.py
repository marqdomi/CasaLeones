# backend/extensions.py

from flask_socketio import SocketIO
from flask_login    import LoginManager
from flask_cors     import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

migrate = Migrate()
# Ya existentes
login_manager = LoginManager()
cors          = CORS()
# Nueva única instancia de DB
db            = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")