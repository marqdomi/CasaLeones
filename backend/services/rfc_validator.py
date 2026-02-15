"""
Sprint 3 — Item 7.4: Validación de RFC y régimen fiscal.

Valida RFC de persona física (13 chars) y moral (12 chars) con:
- Regex estructura
- Dígito verificador (módulo 11 SAT)
- Detección de RFC genéricos (público general / extranjeros)
- Catálogos SAT de regímenes y usos CFDI
"""
import re
import json
import os
import logging

logger = logging.getLogger(__name__)

# ---------- Cargar catálogos SAT ----------
_CATALOGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'catalogos_sat.json')

try:
    with open(_CATALOGS_PATH, 'r', encoding='utf-8') as f:
        CATALOGOS_SAT = json.load(f)
except FileNotFoundError:
    logger.warning('catalogos_sat.json no encontrado, usando catálogos vacíos.')
    CATALOGOS_SAT = {
        'regimenes_fiscales': {},
        'usos_cfdi': {},
        'regimenes_persona_fisica': [],
        'regimenes_persona_moral': [],
        'usos_cfdi_persona_fisica': [],
        'usos_cfdi_persona_moral': [],
    }


# ---------- Constantes ----------
# RFC genérico público general (ventas sin RFC)
RFC_PUBLICO_GENERAL = 'XAXX010101000'
# RFC genérico extranjero
RFC_EXTRANJERO = 'XEXX010101000'

# Patrones de estructura RFC
_RFC_FISICA_RE = re.compile(
    r'^[A-ZÑ&]{4}\d{6}[A-Z\d]{3}$'
)
_RFC_MORAL_RE = re.compile(
    r'^[A-ZÑ&]{3}\d{6}[A-Z\d]{3}$'
)

# Tabla para cálculo de dígito verificador SAT
_CHAR_VALUES = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, 'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14,
    'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19, 'K': 20, 'L': 21,
    'M': 22, 'N': 23, '&': 24, 'O': 25, 'P': 26, 'Q': 27, 'R': 28,
    'S': 29, 'T': 30, 'U': 31, 'V': 32, 'W': 33, 'X': 34, 'Y': 35,
    'Z': 36, ' ': 37, 'Ñ': 38,
}


def _calcular_digito_verificador(rfc_sin_digito: str) -> str:
    """
    Calcula el dígito verificador del RFC usando módulo 11 del SAT.
    El RFC sin dígito debe tener 12 chars (persona física) o 11 chars (persona moral).
    Se le antepone un espacio a persona moral para que quede de 12.
    """
    if len(rfc_sin_digito) == 11:
        rfc_sin_digito = ' ' + rfc_sin_digito

    if len(rfc_sin_digito) != 12:
        return ''

    suma = 0
    for i, char in enumerate(rfc_sin_digito):
        valor = _CHAR_VALUES.get(char.upper(), 0)
        suma += valor * (13 - i)

    residuo = suma % 11
    if residuo == 0:
        return '0'
    diff = 11 - residuo
    if diff == 10:
        return 'A'
    return str(diff)


def normalizar_rfc(rfc: str) -> str:
    """Normaliza un RFC: quita espacios, guiones, convierte a mayúsculas."""
    if not rfc:
        return ''
    return re.sub(r'[\s\-]', '', rfc.strip()).upper()


def validar_rfc(rfc: str) -> tuple[bool, str]:
    """
    Valida un RFC mexicano.

    Returns:
        (es_valido, mensaje_error)
    """
    rfc = normalizar_rfc(rfc)

    if not rfc:
        return False, 'RFC es requerido.'

    # RFC genéricos son válidos
    if rfc in (RFC_PUBLICO_GENERAL, RFC_EXTRANJERO):
        return True, ''

    # Persona física: 13 chars, persona moral: 12 chars
    if len(rfc) == 13:
        if not _RFC_FISICA_RE.match(rfc):
            return False, 'Formato de RFC persona física inválido (debe ser 4 letras + 6 dígitos + 3 alfanuméricos).'
    elif len(rfc) == 12:
        if not _RFC_MORAL_RE.match(rfc):
            return False, 'Formato de RFC persona moral inválido (debe ser 3 letras + 6 dígitos + 3 alfanuméricos).'
    else:
        return False, 'RFC debe tener 12 caracteres (persona moral) o 13 (persona física).'

    # Validar fecha implícita (posiciones 4-5 o 3-4 para moral: AAMMDD)
    if len(rfc) == 13:
        fecha_str = rfc[4:10]
    else:
        fecha_str = rfc[3:9]

    aa = int(fecha_str[0:2])
    mm = int(fecha_str[2:4])
    dd = int(fecha_str[4:6])

    if mm < 1 or mm > 12:
        return False, 'RFC contiene un mes inválido.'
    if dd < 1 or dd > 31:
        return False, 'RFC contiene un día inválido.'

    # Dígito verificador (módulo 11)
    rfc_sin_digito = rfc[:-1]
    digito_esperado = _calcular_digito_verificador(rfc_sin_digito)
    if rfc[-1] != digito_esperado:
        return False, 'Dígito verificador del RFC inválido.'

    return True, ''


def es_persona_fisica(rfc: str) -> bool:
    """True si el RFC es de persona física (13 chars)."""
    return len(normalizar_rfc(rfc)) == 13


def es_persona_moral(rfc: str) -> bool:
    """True si el RFC es de persona moral (12 chars)."""
    return len(normalizar_rfc(rfc)) == 12


def es_rfc_generico(rfc: str) -> bool:
    """True si el RFC es uno de los genéricos del SAT."""
    return normalizar_rfc(rfc) in (RFC_PUBLICO_GENERAL, RFC_EXTRANJERO)


def obtener_regimenes(rfc: str = '') -> dict:
    """
    Retorna los regímenes fiscales válidos para el tipo de persona.
    Si no se puede determinar, retorna todos.
    """
    rfc = normalizar_rfc(rfc)
    todos = CATALOGOS_SAT.get('regimenes_fiscales', {})

    if es_persona_fisica(rfc):
        keys = CATALOGOS_SAT.get('regimenes_persona_fisica', [])
        return {k: v for k, v in todos.items() if k in keys}
    elif es_persona_moral(rfc):
        keys = CATALOGOS_SAT.get('regimenes_persona_moral', [])
        return {k: v for k, v in todos.items() if k in keys}
    return todos


def obtener_usos_cfdi(rfc: str = '') -> dict:
    """
    Retorna los usos de CFDI válidos para el tipo de persona.
    Si no se puede determinar, retorna todos.
    """
    rfc = normalizar_rfc(rfc)
    todos = CATALOGOS_SAT.get('usos_cfdi', {})

    if es_persona_fisica(rfc):
        keys = CATALOGOS_SAT.get('usos_cfdi_persona_fisica', [])
        return {k: v for k, v in todos.items() if k in keys}
    elif es_persona_moral(rfc):
        keys = CATALOGOS_SAT.get('usos_cfdi_persona_moral', [])
        return {k: v for k, v in todos.items() if k in keys}
    return todos


def validar_regimen_fiscal(regimen: str, rfc: str = '') -> tuple[bool, str]:
    """Valida que el régimen fiscal sea válido para el tipo de persona."""
    if not regimen:
        return False, 'Régimen fiscal es requerido.'

    regimenes_validos = obtener_regimenes(rfc)
    if regimen not in regimenes_validos:
        return False, f'Régimen fiscal {regimen} no es válido para este tipo de contribuyente.'
    return True, ''


def validar_uso_cfdi(uso: str, rfc: str = '') -> tuple[bool, str]:
    """Valida que el uso CFDI sea válido para el tipo de persona."""
    if not uso:
        return False, 'Uso de CFDI es requerido.'

    usos_validos = obtener_usos_cfdi(rfc)
    if uso not in usos_validos:
        return False, f'Uso CFDI {uso} no es válido para este tipo de contribuyente.'
    return True, ''
