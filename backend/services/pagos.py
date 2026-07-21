"""Métodos de pago que acepta el negocio.

No todos los negocios aceptan lo mismo: el puesto que estrena el sistema cobra en
efectivo y por transferencia, pero no tiene terminal. Dejar botones que nadie debe
tocar invita a errores que además no se pueden detectar — un cobro marcado como
tarjeta no tiene nada físico que contar contra él en el corte.
"""
from backend.models.models import ConfiguracionSistema

# Etiqueta e ícono (lucide) de cada método soportado por el sistema.
METODOS = {
    'efectivo':      {'label': 'Efectivo',      'icono': 'banknote'},
    'transferencia': {'label': 'Transferencia', 'icono': 'smartphone'},
    'tarjeta':       {'label': 'Tarjeta',       'icono': 'credit-card'},
}

# Sin configurar: efectivo y transferencia. La terminal se habilita cuando exista.
_DEFAULT = 'efectivo,transferencia'

# Métodos cuyo dinero no está en la mano al cobrar y hay que confirmar aparte.
REQUIEREN_VERIFICACION = {'transferencia'}


def metodos_pago_habilitados():
    """Lista de claves habilitadas, en el orden en que se muestran al cobrar."""
    crudo = ConfiguracionSistema.get('metodos_pago', _DEFAULT) or _DEFAULT
    elegidos = [m.strip() for m in crudo.split(',') if m.strip() in METODOS]
    return elegidos or ['efectivo']


def metodos_pago_detalle():
    """Los métodos habilitados con su etiqueta e ícono, para pintar la pantalla."""
    return [
        {'clave': clave, **METODOS[clave],
         'requiere_verificacion': clave in REQUIEREN_VERIFICACION}
        for clave in metodos_pago_habilitados()
    ]
