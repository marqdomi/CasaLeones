from app import create_app
from models.models import db, Usuario

def seed_users():
    usuarios_data = [
        {'nombre': 'Mesero Uno', 'email': 'mesero1@casa.com', 'password': 'password1', 'rol': 'mesero'},
        {'nombre': 'Mesero Dos', 'email': 'mesero2@casa.com', 'password': 'password2', 'rol': 'mesero'},
        {'nombre': 'Mesero Tres', 'email': 'mesero3@casa.com', 'password': 'password3', 'rol': 'mesero'},
        {'nombre': 'Taquero Uno', 'email': 'taquero1@casa.com', 'password': 'password4', 'rol': 'taquero'},
        {'nombre': 'Comal Uno', 'email': 'comal1@casa.com', 'password': 'password5', 'rol': 'comal'},
        {'nombre': 'Administrador', 'email': 'admin@casa.com', 'password': 'adminpass', 'rol': 'admin'},
    ]

    for data in usuarios_data:
        usuario = Usuario.query.filter_by(email=data['email']).first()
        if not usuario:
            usuario = Usuario(
                nombre=data['nombre'],
                email=data['email'],
                rol=data['rol']
            )
            usuario.set_password(data['password'])
            db.session.add(usuario)
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_users()