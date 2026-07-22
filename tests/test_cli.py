"""Comandos de consola — recuperar acceso cuando nadie puede entrar al sistema.

Si estos comandos se rompen, el negocio se queda fuera de su propio POS y la
única salida es entrar a mano a la base de datos.
"""
from backend.models.models import AuditLog, Usuario


class TestListarUsuarios:
    def test_muestra_correo_y_rol(self, app, admin_user):
        resultado = app.test_cli_runner().invoke(args=['usuarios'])
        assert resultado.exit_code == 0
        assert 'admin_test@test.com' in resultado.output
        assert 'admin' in resultado.output

    def test_base_vacia_no_truena(self, app, db):
        resultado = app.test_cli_runner().invoke(args=['usuarios'])
        assert resultado.exit_code == 0
        assert 'No hay usuarios' in resultado.output


class TestResetPassword:
    def test_cambia_la_contrasena(self, app, db, admin_user):
        resultado = app.test_cli_runner().invoke(
            args=['reset-password', 'admin_test@test.com', '--password', 'NuevaClave2026'])
        assert resultado.exit_code == 0

        usuario = Usuario.query.filter_by(email='admin_test@test.com').first()
        assert usuario.check_password('NuevaClave2026')
        assert not usuario.check_password('Test1234!')

    def test_rechaza_contrasena_debil(self, app, db, admin_user):
        resultado = app.test_cli_runner().invoke(
            args=['reset-password', 'admin_test@test.com', '--password', '12345'])
        assert resultado.exit_code != 0

        # La contraseña anterior sigue sirviendo: no se guardó nada a medias.
        usuario = Usuario.query.filter_by(email='admin_test@test.com').first()
        assert usuario.check_password('Test1234!')

    def test_correo_inexistente_lo_dice(self, app, db):
        resultado = app.test_cli_runner().invoke(
            args=['reset-password', 'nadie@test.com', '--password', 'NuevaClave2026'])
        assert resultado.exit_code != 0
        assert 'No existe' in resultado.output

    def test_queda_en_auditoria(self, app, db, admin_user):
        app.test_cli_runner().invoke(
            args=['reset-password', 'admin_test@test.com', '--password', 'NuevaClave2026'])

        logs = AuditLog.query.filter_by(entidad='Usuario', entidad_id=admin_user.id).all()
        assert any('consola' in (log.descripcion or '') for log in logs)


class TestCobroLegacyRetirado:
    """La ruta vieja guardaba el monto recibido (con el cambio incluido) como pago,
    lo que inflaba el corte de caja. Ya no debe existir."""

    def test_ruta_no_existe(self, app):
        rutas = [str(regla) for regla in app.url_map.iter_rules()]
        assert '/meseros/ordenes/<int:orden_id>/cobrar' not in rutas
