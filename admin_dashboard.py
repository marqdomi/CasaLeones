# admin.py
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from backend.app import create_app, socketio
from backend.models.database import db
from backend.models.models import Usuario, Categoria, Producto, Mesa, Silla, Orden, OrdenDetalle

# Crear la aplicación
app = create_app()

# Crear instancia de Admin con el tema Bootswatch (puedes cambiar el template_mode si lo deseas)
admin = Admin(app, name='Panel Admin Restaurante', template_mode='bootstrap4')

# Agregar vistas para cada modelo
admin.add_view(ModelView(Usuario, db.session))
admin.add_view(ModelView(Categoria, db.session))
admin.add_view(ModelView(Producto, db.session))
admin.add_view(ModelView(Mesa, db.session))
admin.add_view(ModelView(Silla, db.session))
admin.add_view(ModelView(Orden, db.session))
admin.add_view(ModelView(OrdenDetalle, db.session))

if __name__ == '__main__':
    # Inicia la aplicación con soporte de SocketIO si es necesario, pero para administración suele ser suficiente Flask
    app.run(debug=True, host='0.0.0.0', port=5005)
    # Alternativamente, puedes usar:
    # socketio.run(app, debug=True, host='0.0.0.0', port=5005)