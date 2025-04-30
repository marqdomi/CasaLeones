document.addEventListener('DOMContentLoaded', () => {
  const modalCobro = document.getElementById('modalCobro');
  const modalContent = document.getElementById('modalCobroBody');

  window.mostrarCobro = async function(ordenId) {
    try {
      const response = await fetch(`/meseros/orden/${ordenId}/info`);
      if (!response.ok) throw new Error('Error al cargar los datos de la orden.');

      const data = await response.json();

      let contenidoHTML = `
        <div class="text-center mb-3">
          <img src="/static/img/logoCasaLeones.svg" alt="Casa Leones Logo" style="max-height: 60px;">
        </div>
        <h5 class="mb-3">Resumen de la orden #${ordenId}</h5>
      `;
      contenidoHTML += `
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Cantidad</th>
              <th>Precio</th>
            </tr>
          </thead>
          <tbody>`;
      let total = 0;
      data.detalles.forEach(item => {
        const subtotal = item.cantidad * item.precio;
        total += subtotal;
        contenidoHTML += `
          <tr>
            <td>${item.nombre}</td>
            <td>${item.cantidad}</td>
            <td>$${subtotal.toFixed(2)}</td>
          </tr>`;
      });

      contenidoHTML += `
          </tbody>
          <tfoot>
            <tr>
              <td colspan="2"><strong>Total</strong></td>
              <td><strong>$${total.toFixed(2)}</strong></td>
            </tr>
          </tfoot>
        </table>
        <div class="text-end">
          <button class="btn btn-primary" onclick="confirmarPago(${ordenId})">Confirmar pago</button>
        </div>
      `;

      modalContent.innerHTML = contenidoHTML;
      const modal = new bootstrap.Modal(modalCobro);
      modal.show();
    } catch (error) {
      alert(error.message);
    }
  };

  window.confirmarPago = async function(ordenId) {
    try {
      const response = await fetch(`/ordenes/${ordenId}/confirmar_pago`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('No se pudo confirmar el pago.');

      // Cierra el modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('modalCobro'));
      modal.hide();

      // Opcional: recargar la página o eliminar visualmente la orden pagada
      location.reload();
    } catch (error) {
      alert(error.message);
    }
  };
});
