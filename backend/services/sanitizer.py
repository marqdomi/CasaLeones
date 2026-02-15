"""Fase 5 — Sprint 1 (4.7): Sanitización de inputs de texto."""
import re
import bleach


def sanitizar_texto(text: str, max_length: int = 500) -> str:
    """Limpia HTML tags, trim whitespace, limita longitud."""
    if not text:
        return ''
    cleaned = bleach.clean(text, tags=[], attributes={}, strip=True)
    return cleaned.strip()[:max_length]


def sanitizar_rfc(rfc: str) -> str:
    """Valida formato básico de RFC y normaliza a mayúsculas.

    Acepta: RFC persona moral (12 chars) y física (13 chars).
    RFC genérico público: XAXX010101000
    RFC genérico extranjero: XEXX010101000
    """
    if not rfc:
        return ''
    rfc = rfc.strip().upper().replace(' ', '').replace('-', '')
    # Validar formato básico
    if not re.match(r'^[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}$', rfc):
        return ''  # Retorna vacío si no es válido
    return rfc[:13]


def sanitizar_email(email: str) -> str:
    """Valida formato básico de email."""
    if not email:
        return ''
    email = email.strip().lower()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return ''
    return email[:254]


def sanitizar_telefono(telefono: str) -> str:
    """Solo permite dígitos, +, (, ), - y espacios."""
    if not telefono:
        return ''
    cleaned = re.sub(r'[^\d+\-() ]', '', telefono)
    return cleaned.strip()[:20]
