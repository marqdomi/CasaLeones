// Asegura que este script se ejecute después de que el DOM esté listo
$(document).ready(function() {
    console.log('meseros.js cargado y DOM listo.');

    // Contenedor para toasts (asegúrate que exista en tu base.html o meseros.html)
    // <div id="toast-container" style="position: fixed; top: 1rem; right: 1rem; z-index: 1050;"></div>
    function showToast(message, type = 'info') { // type puede ser 'info', 'success', 'warning', 'danger'
        const container = $('#toast-container');
        if (!container.length) {
            $('body').append('<div id="toast-container" style="position: fixed; top: 1rem; right: 1rem; z-index: 1050;"></div>');
        }
        
        let bgColorClass = 'bg-primary'; // Default Bootstrap primary
        if (type === 'success') bgColorClass = 'bg-success';
        if (type === 'warning') bgColorClass = 'bg-warning text-dark'; // text-dark para mejor contraste en warning
        if (type === 'danger') bgColorClass = 'bg-danger';

        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgColorClass} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`;
        
        $('#toast-container').append(toastHtml);
        const toastElement = new bootstrap.Toast(document.getElementById(toastId));
        toastElement.show();
        // Limpiar el toast del DOM después de que se oculte para evitar acumulación
        document.getElementById(toastId).addEventListener('hidden.bs.toast', function () {
            $(this).remove();
        });
    }

    // Inicialización de Socket.IO
    if (typeof io !== 'undefined') {
        const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

        socket.on('connect', () => {
            console.log('Socket.IO conectado desde meseros.js');
        });

        socket.on('disconnect', () => {
            console.log('Socket.IO desconectado desde meseros.js');
        });

        // Cuando llega una nueva orden a cocina (emitido por el propio mesero al enviar)
        socket.on('nueva_orden_cocina', function(data) {
            console.log('Evento nueva_orden_cocina recibido en meseros.js:', data);
            // Originalmente recargaba. Por ahora, solo mostramos toast.
            // La actualización de la lista de órdenes del mesero ocurre si él mismo creó la orden y fue redirigido.
            // Si otro mesero crea una orden, este mesero no verá esa orden hasta recargar,
            // a menos que implementemos una adición dinámica a la tabla de órdenes.
            showToast(`Nueva orden #${data.orden_id} enviada a cocina.`, 'info');
            // Considerar recargar o actualizar la tabla de órdenes activas aquí si es necesario
            // para ver órdenes de otros meseros en un entorno multi-mesero,
            // o si la creación no causa una redirección que ya refresque.
            // Por ahora, si la creación de orden causa una redirección a detalle_orden y luego
            // vuelve a meseros.html, la lista se refrescará.
        });

        // Cuando un ítem está listo en cocina
        socket.on('item_listo_notificacion', function(data) {
            console.log('Evento item_listo_notificacion recibido en meseros.js:', data);
            // data contiene: item_id (es el detalle_id), orden_id, producto_nombre, mesa_nombre
            showToast(`¡${data.producto_nombre} de orden #${data.orden_id} está listo!`, 'success');

            var detalleRow = $('#product-item-' + data.item_id); 
            if (detalleRow.length) {
                detalleRow.find('.estado-producto-texto')
                          .empty() // Limpiar contenido anterior
                          .append($('<span>').addClass('badge bg-success').text('Listo en cocina'));
                
                detalleRow.find('.accion-producto').html(
                    `<button class="btn btn-sm btn-primary btn-entregar-item" 
                             data-detalle-id="${data.item_id}" 
                             data-orden-id="${data.orden_id}">
                        Entregar
                     </button>`
                );
                
                // Cambiar clase de la fila para posible estilizado
                detalleRow.removeClass('detalle-pendiente-cocina detalle-entregado').addClass('detalle-listo-cocina');
                
                verificarEstadoParaCobro(data.orden_id); // Verificar si se puede cobrar
            } else {
                console.warn('No se encontró la fila del detalle #product-item-' + data.item_id + ' para actualizar.');
            }
        });

        // Cuando la orden completa está lista desde cocina (todos los ítems para cocina están listos)
        socket.on('orden_completa_lista', function(data) {
            console.log('Evento orden_completa_lista recibido en meseros.js:', data);
            showToast(`¡Orden #${data.orden_id} completamente lista en cocina!`, 'success');
            
            var ordenAcordeonItem = $('#orden-acordeon-' + data.orden_id);
            if (ordenAcordeonItem.length) {
                // Podrías cambiar el estilo del header del acordeón para la orden
                ordenAcordeonItem.find('.accordion-button').addClass('text-primary fw-bold'); // Ejemplo
                 // La lógica de habilitar "Cobrar" se maneja por verificarEstadoParaCobro
            }
        });

        // Cuando la orden ha sido completamente entregada y su estado cambia (emitido por el backend)
        socket.on('orden_actualizada_para_cobro', function(data) {
            console.log('Evento orden_actualizada_para_cobro recibido:', data);
            if (data.estado_orden === 'completada') {
                showToast(`Orden #${data.orden_id} lista para cobro.`, 'info');
                verificarEstadoParaCobro(data.orden_id); // Esto debería habilitar el botón Cobrar
            }
            // Podrías querer actualizar el texto del estado general de la orden en la tabla principal.
            $('#orden-header-' + data.orden_id).find('td').eq(2).text(data.estado_orden.charAt(0).toUpperCase() + data.estado_orden.slice(1));
        });

    } else {
        console.warn('Socket.IO no está definido. Las actualizaciones en tiempo real no funcionarán.');
    }

    // Delegación de eventos para el clic en ".btn-entregar-item"
    // Asumiendo que #meseros-dashboard es un contenedor estático para las órdenes
    $('#meseros-dashboard').on('click', '.btn-entregar-item', function(e) {
        e.stopPropagation(); // Prevenir que se cierre el acordeón si el botón está en el header (no es el caso aquí)
        
        var detalleId = $(this).data('detalle-id');
        var ordenId = $(this).data('orden-id');
        var botonClickeado = $(this);

        if (!detalleId || !ordenId) {
            console.error('Error: detalleId u ordenId no encontrados en el botón Entregar.');
            alert('Error interno al intentar entregar el ítem.');
            return;
        }

        console.log(`Intentando marcar como entregado: ordenId=${ordenId}, detalleId=${detalleId}`);

        $.ajax({
            type: 'POST',
            url: `/meseros/entregar_item/${ordenId}/${detalleId}`, // Endpoint que definimos
            success: function(response) {
                if (response.success) {
                    console.log('Ítem ' + detalleId + ' marcado como entregado exitosamente.');
                    showToast(response.message || 'Ítem entregado.', 'success');
                    
                    var detalleRow = $('#product-item-' + detalleId);
                    if (detalleRow.length) {
                        detalleRow.find('.estado-producto-texto')
                                  .empty()
                                  .append($('<span>').addClass('badge bg-secondary').text('Entregado'));
                        
                        detalleRow.find('.accion-producto')
                                  .html($('<span>').addClass('text-success fw-bold').html('Entregado <i class="fas fa-check"></i>')); // Añadí un ícono
                        
                        detalleRow.removeClass('detalle-listo-cocina detalle-pendiente-cocina').addClass('detalle-entregado');
                    }
                    verificarEstadoParaCobro(ordenId);
                } else {
                    alert(response.message || 'Error al marcar el ítem como entregado.');
                }
            },
            error: function(xhr, status, error) {
                console.error("Error AJAX al entregar ítem:", status, error, xhr.responseText);
                let errorMsg = 'Error de comunicación al entregar el ítem.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }
                alert(errorMsg);
            }
        });
    });

    // Funciones para el Modal de Cobro (adaptadas de tu meseros.js)
    window.mostrarCobro = async function(ordenId) {
        const modalContent = $('#modalCobroBody');
        const modalElement = document.getElementById('modalCobro');
        if (!modalContent.length || !modalElement) {
            console.error('Elementos del modal de cobro no encontrados.');
            return;
        }
        modalContent.html(`
            <div class="text-center py-3">
                <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
                <p class="mt-2">Cargando detalle...</p>
            </div>`);
        
        const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
        modalInstance.show();

        try {
            const response = await fetch(`/meseros/ordenes/${ordenId}/cobrar_info`); // Usar cobrar_info
            if (!response.ok) throw new Error(`Error al cargar datos de la orden (${response.status})`);
            const data = await response.json();

            let contenidoHTML = `
                <div class="text-center mb-3">
                    <img src="/static/img/logoCasaLeones.svg" alt="Casa Leones Logo" style="max-height: 50px;">
                </div>
                <h5 class="mb-3">Resumen de la orden #${data.orden_id}</h5>
                <div class="ticket">`;
            let total = 0;
            // Agrupar para el ticket visual
            const grouped = {};
            data.detalles.forEach(item => {
                if (!grouped[item.nombre]) {
                    grouped[item.nombre] = { cantidad: 0, precio: item.precio, entregado: item.entregado, estado: item.estado };
                }
                grouped[item.nombre].cantidad += item.cantidad;
                // Si algún ítem del grupo no está entregado, el grupo no está completamente entregado
                if (item.estado !== 'entregado') { 
                    grouped[item.nombre].parcialmente_entregado = true;
                }
            });

            for (const [nombre, info] of Object.entries(grouped)) {
                const subtotal = info.cantidad * info.precio;
                total += subtotal;
                contenidoHTML += `
                    <div class="ticket-item">
                        ${nombre} - ${info.cantidad} x $${info.precio.toFixed(2)} = $${subtotal.toFixed(2)}
                        ${info.parcialmente_entregado ? '<small class="text-danger ms-2">(Algunos pendientes de entrega)</small>' : ''}
                    </div>`;
            }
            contenidoHTML += `
                <hr>
                <div class="ticket-total d-flex justify-content-between">
                    <strong>Total</strong>
                    <strong>$${total.toFixed(2)}</strong>
                </div>
                </div>
                <div class="mt-3 mb-3">
                    <label for="monto_recibido_modal_${ordenId}">Monto recibido:</label>
                    <input type="number" step="0.01" id="monto_recibido_modal_${ordenId}" class="form-control">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-success btn-confirmar-pago-modal" data-orden-id="${ordenId}">Confirmar Pago</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                </div>`;
            modalContent.html(contenidoHTML);
            
            // Adjuntar listener al nuevo botón de confirmar pago
            modalContent.find('.btn-confirmar-pago-modal').on('click', procesarPagoDesdeModal);

        } catch (error) {
            console.error('Error en mostrarCobro:', error);
            modalContent.html(`<p class="text-danger">Error al cargar detalles: ${error.message}</p>`);
        }
    };
    
    // Nueva función para manejar el clic del botón de pago DENTRO del modal
    async function procesarPagoDesdeModal(event) {
        const boton = $(event.target);
        const ordenId = boton.data('orden-id');
        const montoRecibidoInput = $(`#monto_recibido_modal_${ordenId}`);
        const montoRecibido = parseFloat(montoRecibidoInput.val());

        const totalText = $('#modalCobroBody .ticket-total strong:last-child').text();
        const total = parseFloat(totalText.replace('$', ''));

        if (isNaN(montoRecibido)) {
            alert('Por favor ingresa un monto recibido válido.');
            montoRecibidoInput.focus();
            return;
        }
        if (montoRecibido < total) {
            alert('El monto recibido es insuficiente.');
            montoRecibidoInput.focus();
            return;
        }

        try {
            const response = await fetch(`/meseros/ordenes/${ordenId}/cobrar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                body: JSON.stringify({ monto_recibido: montoRecibido })
            });
            
            const data = await response.json(); // Intenta parsear JSON siempre

            if (!response.ok) {
                throw new Error(data.message || data.error || `Error ${response.status} al procesar el pago.`);
            }
            
            const modalCobroEl = document.getElementById('modalCobro');
            const modalInstance = bootstrap.Modal.getInstance(modalCobroEl);
            if (modalInstance) modalInstance.hide();

            showToast(`Pago registrado para orden #${ordenId}. Cambio: $${data.cambio.toFixed(2)}`, 'success');
            // Actualizar la UI para reflejar que la orden está pagada
            var ordenAcordeonItem = $('#orden-acordeon-' + ordenId);
            if(ordenAcordeonItem.length){
                ordenAcordeonItem.find('.accordion-button').removeClass('text-primary fw-bold').addClass('text-muted');
                ordenAcordeonItem.find('td').eq(2).text('Pagada'); // Actualiza estado en tabla principal
                ordenAcordeonItem.find('.btn-cobrar-orden').remove(); // Quita botón cobrar
                ordenAcordeonItem.find('.btn-modificar-orden').remove(); // Quita botón modificar
                // Podrías colapsar el acordeón y/o quitarlo de la lista de "activas"
                // Para una actualización completa, window.location.reload() es lo más simple.
                setTimeout(() => window.location.reload(), 1500); // Recargar después de mostrar el toast
            }

        } catch (error) {
            console.error('Error en procesarPagoDesdeModal:', error);
            alert(error.message);
        }
    }

    // Limpieza de backdrop del modal (ya lo tenías, está bien)
    const modalCobroEl = document.getElementById('modalCobro');
    if (modalCobroEl) {
        modalCobroEl.addEventListener('hidden.bs.modal', () => {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        });
    }

    // Función para verificar si el botón "Cobrar" de una orden debe habilitarse
    window.verificarEstadoParaCobro = function(ordenId) {
        var ordenAcordeonItem = $('#orden-acordeon-' + ordenId);
        if (!ordenAcordeonItem.length) {
            console.warn('verificarEstadoParaCobro: No se encontró #orden-acordeon-' + ordenId);
            return;
        }

        var todosEntregados = true;
        var itemsEnOrden = ordenAcordeonItem.find('.product-row .estado-producto-texto');
        
        if (itemsEnOrden.length === 0) { // Si no hay items listados (ej. orden nueva sin detalles)
            todosEntregados = false;
        } else {
            itemsEnOrden.each(function() {
                if ($(this).text().trim().toLowerCase() !== 'entregado') {
                    todosEntregados = false;
                    return false; // Rompe el bucle .each
                }
            });
        }

        var botonCobrar = ordenAcordeonItem.find('.btn-cobrar-orden'); // Asumo que el botón Cobrar está DENTRO del acordeón
        if (botonCobrar.length) {
            if (todosEntregados) {
                botonCobrar.prop('disabled', false)
                           .removeClass('btn-outline-secondary disabled') // Clases para deshabilitado
                           .addClass('btn-success'); // Clase para habilitado
                console.log('Botón Cobrar HABILITADO para orden ' + ordenId);
            } else {
                botonCobrar.prop('disabled', true)
                           .removeClass('btn-success')
                           .addClass('btn-outline-secondary disabled');
                console.log('Botón Cobrar DESHABILITADO para orden ' + ordenId);
            }
        } else {
            console.warn('verificarEstadoParaCobro: No se encontró .btn-cobrar-orden para orden ' + ordenId);
        }
    }
    
    // Llamar a verificarEstadoParaCobro para todas las órdenes visibles en la carga inicial de la página
    $('.accordion-item[id^="orden-acordeon-"]').each(function() {
        var ordenId = $(this).attr('id').replace('orden-acordeon-', '');
        if (ordenId) {
            verificarEstadoParaCobro(ordenId);
        }
    });

}); // Fin de $(document).ready