from flask import Flask

from backend.models.models import Usuario
from backend.models.database import init_db
from backend.extensions import db
from backend.extensions import socketio, login_manager, cors
from backend.routes.auth import auth_bp
from backend.routes.cocina import cocina_bp
from backend.routes.meseros import meseros_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.api import api_bp
from backend.routes.orders import orders_bp

login_manager.login_view = 'auth.login'

def load_user(user_id):
    return Usuario.query.get(int(user_id))

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    # Disable caching of static files in development
    if app.config.get('DEBUG'):
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['EXPLAIN_TEMPLATE_LOADING'] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    # Disable Jinja2 template caching for development
    app.jinja_env.cache.clear()

    login_manager.user_loader(load_user)

    with app.app_context():
        init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(cocina_bp, url_prefix="/cocina")
    app.register_blueprint(meseros_bp, url_prefix='/meseros')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp)
    app.register_blueprint(orders_bp)

    #print(app.url_map)
    return app

if __name__ == "__main__":
    app = create_app()
    # Usamos socketio.run si se utiliza Flask-SocketIO, o app.run en su defecto
    # socketio.run(app, debug=True, host='0.0.0.0', port=5005)
    socketio.run(app, debug=True, host='0.0.0.0', port=5005)