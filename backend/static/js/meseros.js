console.log('meseros.js loaded, typeof marcarEntregado:', typeof window.marcarEntregado);
// Function to display Bootstrap toasts for real-time notifications
function showToast(message) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toastEl = document.createElement('div');
  toastEl.className = 'toast align-items-center text-white bg-primary border-0';
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>`;
  container.appendChild(toastEl);
  const bsToast = new bootstrap.Toast(toastEl);
  bsToast.show();
}
// Initialize Socket.IO for real-time order updates (guarded for environments where io is not available)
if (typeof io !== 'undefined') {
  const socket = io();
  // Show toast for new orders and item readiness
  socket.on('nueva_orden_cocina', (data) => {
    showToast(`¡Nueva orden #${data.orden_id}!`);
  });
  socket.on('item_listo_notificacion', (data) => {
    showToast(`Producto listo: ${data.producto_nombre}`);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const modalCobro = document.getElementById('modalCobro');
  const modalContent = document.getElementById('modalCobroBody');

  // Abre el modal con el resumen de la orden y el formulario de pago
  window.mostrarCobro = async function(ordenId) {
    try {
      const response = await fetch(`/meseros/ordenes/${ordenId}/detalles_json`);
      if (!response.ok) throw new Error('Error al cargar los datos de la orden.');

      const data = await response.json();

      let contenidoHTML = `
        <div class="text-center mb-3">
          <img src="/static/img/logoCasaLeones.svg" alt="Casa Leones Logo" style="max-height: 60px;">
        </div>
        <h5 class="mb-3">Resumen de la orden #${ordenId}</h5>
      `;
      let total = 0;
      // Build a grouped ticket-style list
      contenidoHTML += '<div class="ticket">';
      // Group items by name
      const grouped = {};
      data.detalles.forEach(item => {
        if (!grouped[item.nombre]) {
          grouped[item.nombre] = { cantidad: 0, precio: item.precio };
        }
        grouped[item.nombre].cantidad += item.cantidad;
      });
      // Render grouped items
      for (const [nombre, info] of Object.entries(grouped)) {
        const subtotal = info.cantidad * info.precio;
        total += subtotal;
        contenidoHTML += `
          <div class="ticket-item">
            ${nombre} - ${info.cantidad} x $${info.precio.toFixed(2)} = $${subtotal.toFixed(2)}
          </div>`;
      }
      // Separator and total line
      contenidoHTML += `
        <hr>
        <div class="ticket-total d-flex justify-content-between">
          <strong>Total</strong>
          <strong>$${total.toFixed(2)}</strong>
        </div>
        </div>`;

      contenidoHTML += `
        <div class="mb-3">
          <label for="monto_recibido">Monto recibido:</label>
          <input type="number" step="0.01" id="monto_recibido" class="form-control">
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-success" id="confirmarPagoBtn" onclick="procesarPago(event)" data-orden-id="${ordenId}">Confirmar Pago</button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        </div>
      `;

      modalContent.innerHTML = contenidoHTML;
      const modal = new bootstrap.Modal(modalCobro);
      modal.show();
    } catch (error) {
      alert(error.message);
    }
  };

  // Envía el pago y muestra el cambio
  window.procesarPago = async function(event) {
    try {
      const btn = event.target;
      const ordenId = btn.getAttribute('data-orden-id');

      const recibido = parseFloat(document.getElementById('monto_recibido').value);
      if (isNaN(recibido)) {
        alert('Por favor ingresa un monto recibido válido.');
        return;
      }

      // Total recalculation removed to avoid conflict with detalle_orden.html summary

      const response = await fetch(`/meseros/ordenes/${ordenId}/cobrar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ monto_recibido: recibido })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'No se pudo confirmar el pago.');
      }

      const data = await response.json();

      // Cierra el modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('modalCobro'));
      modal.hide();

      alert(`Pago registrado. Cambio: $${data.cambio.toFixed(2)}`);
      // Opcional: volver a cargar la lista de órdenes
      window.location.reload();
    } catch (error) {
      alert(error.message);
    }
  };

  // Limpia backdrop sobrante al cerrar el modal de cobro
  const modalCobroEl = document.getElementById('modalCobro');
  if (modalCobroEl) {
    modalCobroEl.addEventListener('hidden.bs.modal', () => {
      document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    });
  }

  // Bind "Entregar" buttons for grouped products
  document.querySelectorAll('.btn-entregar-grupo').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const ordenId = btn.getAttribute('data-orden-id');
      const productoId = btn.getAttribute('data-producto-id');
      window.marcarEntregadoGrupo(ordenId, productoId);
    });
  });
});

/* Commented out original marcarEntregado to use group version instead
window.marcarEntregado = function(ordenId, detalleId) {
  console.log('window.marcarEntregado invoked with ordenId=', ordenId, 'detalleId=', detalleId);
  fetch(`/meseros/ordenes/${ordenId}/producto/${detalleId}/entregar`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({})
  })
  .then(response => {
    if (response.status === 401) {
      alert('Sesión expirada. Por favor inicia sesión de nuevo.');
      throw new Error('401');
    }
    if (response.status === 403) {
      alert('No tienes permiso para realizar esta acción.');
      throw new Error('403');
    }
    if (!response.ok) {
      return response.json().then(data => {
        const msg = data.error || `Error ${response.status}`;
        alert(msg);
        throw new Error(msg);
      });
    }
    return response.json();
  })
  .then(data => {
    if (data.success) {
      document.getElementById(`estado-detalle-${detalleId}`).textContent = 'entregado';
    } else {
      alert(data.message || 'Error al marcar entregado');
    }
  })
  .catch(err => console.error(err));
};
*/

window.marcarEntregadoGrupo = function(ordenId, productoId) {
  fetch(`/meseros/ordenes/${ordenId}/entregar/${productoId}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({})
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => { throw new Error(data.error || 'Error'); });
    }
    return response.json();
  })
  .then(data => {
    window.location.reload();
    const statusEl = document.getElementById(`estado-orden-${ordenId}-producto-${productoId}`);
    if (statusEl) {
      statusEl.textContent = 'listo';
      const actionCell = statusEl.nextElementSibling;
      if (actionCell) {
        actionCell.innerHTML = '<span class="text-success">Entregado</span>';
      }
    }
  })
  .catch(err => alert(err.message));
};
