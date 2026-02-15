/**
 * Sprint 3 — Item 7.4: Validación de RFC en el cliente.
 * Auto-uppercase, trim, validación de estructura + dígito verificador.
 */
(function () {
  'use strict';

  const RFC_PUBLICO = 'XAXX010101000';
  const RFC_EXTRANJERO = 'XEXX010101000';

  const RFC_FISICA_RE = /^[A-ZÑ&]{4}\d{6}[A-Z\d]{3}$/;
  const RFC_MORAL_RE = /^[A-ZÑ&]{3}\d{6}[A-Z\d]{3}$/;

  const CHAR_VALUES = {
    '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
    'A':10,'B':11,'C':12,'D':13,'E':14,'F':15,'G':16,'H':17,'I':18,
    'J':19,'K':20,'L':21,'M':22,'N':23,'&':24,'O':25,'P':26,'Q':27,
    'R':28,'S':29,'T':30,'U':31,'V':32,'W':33,'X':34,'Y':35,'Z':36,
    ' ':37,'Ñ':38
  };

  function calcularDigitoVerificador(rfcSinDigito) {
    if (rfcSinDigito.length === 11) rfcSinDigito = ' ' + rfcSinDigito;
    if (rfcSinDigito.length !== 12) return '';
    let suma = 0;
    for (let i = 0; i < rfcSinDigito.length; i++) {
      const val = CHAR_VALUES[rfcSinDigito[i].toUpperCase()] || 0;
      suma += val * (13 - i);
    }
    const residuo = suma % 11;
    if (residuo === 0) return '0';
    const diff = 11 - residuo;
    return diff === 10 ? 'A' : String(diff);
  }

  function normalizarRFC(rfc) {
    return (rfc || '').replace(/[\s\-]/g, '').toUpperCase().trim();
  }

  /**
   * Valida un RFC mexicano.
   * @param {string} rfc
   * @returns {{valid: boolean, error: string}}
   */
  function validarRFC(rfc) {
    rfc = normalizarRFC(rfc);
    if (!rfc) return { valid: false, error: 'RFC es requerido.' };

    if (rfc === RFC_PUBLICO || rfc === RFC_EXTRANJERO) {
      return { valid: true, error: '' };
    }

    if (rfc.length === 13) {
      if (!RFC_FISICA_RE.test(rfc)) {
        return { valid: false, error: 'Formato RFC persona física inválido.' };
      }
    } else if (rfc.length === 12) {
      if (!RFC_MORAL_RE.test(rfc)) {
        return { valid: false, error: 'Formato RFC persona moral inválido.' };
      }
    } else {
      return { valid: false, error: 'RFC debe tener 12 o 13 caracteres.' };
    }

    // Validar fecha
    const fechaStr = rfc.length === 13 ? rfc.substring(4, 10) : rfc.substring(3, 9);
    const mm = parseInt(fechaStr.substring(2, 4), 10);
    const dd = parseInt(fechaStr.substring(4, 6), 10);
    if (mm < 1 || mm > 12) return { valid: false, error: 'RFC contiene un mes inválido.' };
    if (dd < 1 || dd > 31) return { valid: false, error: 'RFC contiene un día inválido.' };

    // Dígito verificador
    const sinDigito = rfc.substring(0, rfc.length - 1);
    const esperado = calcularDigitoVerificador(sinDigito);
    if (rfc[rfc.length - 1] !== esperado) {
      return { valid: false, error: 'Dígito verificador del RFC inválido.' };
    }

    return { valid: true, error: '' };
  }

  /**
   * Inicializa validación en tiempo real para campos RFC.
   * Busca inputs con [data-rfc-validate] y agrega listeners.
   */
  function initRFCValidation() {
    document.querySelectorAll('[data-rfc-validate]').forEach(function (input) {
      // Auto-uppercase al escribir
      input.addEventListener('input', function () {
        const pos = this.selectionStart;
        this.value = normalizarRFC(this.value);
        this.setSelectionRange(pos, pos);
      });

      // Validar al salir del campo
      input.addEventListener('blur', function () {
        const val = this.value.trim();
        if (!val) {
          this.classList.remove('is-invalid', 'is-valid');
          removeFeedback(this);
          return;
        }
        const result = validarRFC(val);
        if (result.valid) {
          this.classList.remove('is-invalid');
          this.classList.add('is-valid');
          showFeedback(this, '', false);
        } else {
          this.classList.remove('is-valid');
          this.classList.add('is-invalid');
          showFeedback(this, result.error, true);
        }
      });
    });
  }

  function showFeedback(input, message, isError) {
    removeFeedback(input);
    if (!message) return;
    const div = document.createElement('div');
    div.className = isError ? 'invalid-feedback' : 'valid-feedback';
    div.textContent = message;
    div.style.display = 'block';
    div.setAttribute('data-rfc-feedback', 'true');
    input.parentNode.appendChild(div);
  }

  function removeFeedback(input) {
    const existing = input.parentNode.querySelector('[data-rfc-feedback]');
    if (existing) existing.remove();
  }

  // Auto-init when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRFCValidation);
  } else {
    initRFCValidation();
  }

  // Expose for programmatic use
  window.RFCValidator = {
    validar: validarRFC,
    normalizar: normalizarRFC,
    initValidation: initRFCValidation
  };
})();
