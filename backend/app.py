from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_cors import CORS

from backend.models.models import Usuario
from backend.models.database import init_db, db

from backend.routes.orders import orders_bp
from backend.routes.meseros import meseros_bp
from backend.routes.cocina import cocina_bp
from backend.routes.auth import auth_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.api import api_bp
from backend.models.models import Orden, OrdenDetalle, Producto
from backend.models.database import db

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

socketio = SocketIO()

def load_user(user_id):
    return Usuario.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['EXPLAIN_TEMPLATE_LOADING'] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    login_manager.user_loader(load_user)
    
    # 🔧 Esta línea soluciona el error:
    app.login_manager = login_manager

    with app.app_context():
        init_db()

    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)
    app.register_blueprint(cocina_bp, url_prefix="/cocina")
    app.register_blueprint(meseros_bp, url_prefix='/meseros')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp)

    #print(app.url_map)
    return app

if __name__ == "__main__":
    app = create_app()
    # Usamos socketio.run si se utiliza Flask-SocketIO, o app.run en su defecto
    # socketio.run(app, debug=True, host='0.0.0.0', port=5005)
    socketio.run(app, debug=True, host='0.0.0.0', port=5005)