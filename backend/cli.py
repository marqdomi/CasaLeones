"""Comandos de consola para operación del sistema.

Sirven para lo que no se puede hacer desde la interfaz porque justamente no se
puede entrar: recuperar el acceso cuando se olvidó la contraseña del admin.

Uso en la instalación con Docker:

    docker compose exec web flask usuarios
    docker compose exec web flask reset-password correo@ejemplo.com
"""
import logging

import click
from flask.cli import with_appcontext

from backend.extensions import db
from backend.models.models import Usuario
from backend.services.audit import registrar_auditoria
from backend.services.password_policy import validar_password

logger = logging.getLogger(__name__)


@click.command('usuarios')
@with_appcontext
def listar_usuarios():
    """Lista los usuarios registrados (para saber con qué correo entrar)."""
    usuarios = Usuario.query.order_by(Usuario.rol, Usuario.nombre).all()
    if not usuarios:
        click.echo('No hay usuarios registrados. ¿Falta completar el asistente inicial?')
        return

    click.echo('')
    click.echo(f"{'CORREO':<35} {'NOMBRE':<25} {'ROL':<15} SUCURSAL")
    click.echo('-' * 90)
    for u in usuarios:
        sucursal = u.sucursal.nombre if u.sucursal_id and u.sucursal else '—'
        click.echo(f'{u.email:<35} {u.nombre:<25} {u.rol:<15} {sucursal}')
    click.echo('')


@click.command('reset-password')
@click.argument('email')
@click.option('--password', help='Contraseña nueva. Si se omite, se pide sin mostrarla en pantalla.')
@with_appcontext
def reset_password(email, password):
    """Cambia la contraseña del usuario con ese correo."""
    usuario = Usuario.query.filter_by(email=email.strip()).first()
    if not usuario:
        raise click.ClickException(
            f'No existe ningún usuario con el correo "{email}". '
            'Usa "flask usuarios" para ver los correos registrados.'
        )

    if not password:
        password = click.prompt('Contraseña nueva', hide_input=True, confirmation_prompt=True)

    valida, errores = validar_password(password, nombre=usuario.nombre, email=usuario.email)
    if not valida:
        for error in errores:
            click.echo(f'  • {error}', err=True)
        raise click.ClickException('La contraseña no cumple los requisitos.')

    usuario.set_password(password)
    registrar_auditoria(
        'editar', 'Usuario', usuario.id,
        f'Contraseña restablecida por consola: {usuario.email}',
        usuario_id=usuario.id,
    )
    db.session.commit()

    click.echo(f'✅ Contraseña actualizada para {usuario.nombre} ({usuario.email}).')


def registrar_comandos(app):
    """Engancha los comandos al `flask` de esta app."""
    app.cli.add_command(listar_usuarios)
    app.cli.add_command(reset_password)
