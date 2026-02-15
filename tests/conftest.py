"""Pytest configuration — CasaLeones POS test suite."""
import os
import pytest

# Use SQLite in-memory for tests
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['FLASK_ENV'] = 'development'
os.environ['REDIS_URL'] = 'redis://localhost:6379'

from backend.app import create_app
from backend.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """Create a Flask app configured for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'SESSION_TYPE': 'filesystem',
        'SERVER_NAME': 'localhost',
    })
    yield app


@pytest.fixture(scope='function')
def db(app):
    """Create fresh database tables for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Test client with clean database."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    from backend.models.models import Usuario
    from werkzeug.security import generate_password_hash

    user = Usuario(
        nombre='Admin Test',
        username='admin_test',
        password=generate_password_hash('Test1234!'),
        rol='admin',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def mesero_user(db):
    """Create and return a mesero user."""
    from backend.models.models import Usuario
    from werkzeug.security import generate_password_hash

    user = Usuario(
        nombre='Mesero Test',
        username='mesero_test',
        password=generate_password_hash('Test1234!'),
        rol='mesero',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def superadmin_user(db):
    """Create and return a superadmin user."""
    from backend.models.models import Usuario
    from werkzeug.security import generate_password_hash

    user = Usuario(
        nombre='Super Admin',
        username='super_test',
        password=generate_password_hash('Test1234!'),
        rol='superadmin',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_producto(db):
    """Create a sample product."""
    from backend.models.models import Producto

    prod = Producto(
        nombre='Taco al Pastor',
        precio=45.00,
        categoria='tacos',
        disponible=True,
    )
    db.session.add(prod)
    db.session.commit()
    return prod


@pytest.fixture
def sample_mesa(db):
    """Create a sample table."""
    from backend.models.models import Mesa

    mesa = Mesa(
        numero=1,
        capacidad=4,
        zona='interior',
        estado='disponible',
    )
    db.session.add(mesa)
    db.session.commit()
    return mesa


def login(client, username, password):
    """Helper to log in a user via the test client."""
    return client.post('/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)
