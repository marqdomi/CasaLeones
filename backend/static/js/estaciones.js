// Initialize Socket.IO for real-time updates (guarded for environments where io is not available)
if (typeof io !== 'undefined') {
  const socket = io();
  socket.on('nueva_orden_cocina', () => {
    window.location.reload();
  });
  socket.on('item_listo_notificacion', () => {
    window.location.reload();
  });
}



document.addEventListener("DOMContentLoaded", () => {
    const finalizarButtons = document.querySelectorAll(".btn-finalizar-producto");
    const marcarEntregadoButtons = document.querySelectorAll(".btn-marcar-entregado");

    finalizarButtons.forEach(button => {
        button.addEventListener("click", () => {
            const ordenId = button.dataset.ordenId;

            fetch(`/estaciones/finalizar_orden/${ordenId}`, {
                method: "POST"
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Error al finalizar la orden.");
                }
            });
        });
    });

    marcarEntregadoButtons.forEach(button => {
        button.addEventListener("click", () => {
            const detalleId = button.dataset.detalleId;

            fetch(`/estaciones/marcar_entregado/${detalleId}`, {
                method: "POST"
            })
            .then(response => {
                if (response.ok) {
                    button.classList.remove("btn-warning");
                    button.classList.add("btn-success");
                    button.textContent = "Entregado";
                    button.disabled = true;
                } else {
                    alert("Error al marcar como entregado.");
                }
            });
        });
    });
});