"""Sprint 6 — Item 6.4: Generador de PDF para reportes con WeasyPrint."""
import logging
from io import BytesIO
from flask import render_template

logger = logging.getLogger(__name__)


def generar_pdf(template_name, **context):
    """Renderiza un template HTML y lo convierte a PDF con WeasyPrint.

    Args:
        template_name: Ruta del template Jinja2 (e.g. 'pdf/ventas.html').
        **context: Variables de contexto para el template.

    Returns:
        bytes del PDF generado, o None si hay error.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        logger.error('WeasyPrint no está instalado. Instale con: pip install WeasyPrint>=60.0')
        return None

    try:
        html_string = render_template(template_name, **context)
        pdf_bytes = HTML(string=html_string).write_pdf()
        return pdf_bytes
    except Exception as e:
        logger.exception('Error al generar PDF con template=%s: %s', template_name, e)
        return None
