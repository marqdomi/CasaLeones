$(document).ready(function() {
    console.log('meseros.js cargado.');

    // =============================================
    // Toast helper (Sprint 5 — improved)
    // =============================================
    function showToast(message, type = 'info') {
        const container = $('#toast-container');
        if (!container.length) {
            $('body').append('<div id="toast-container" class="position-fixed top-0 end-0 p-3" style="z-index:1200;" role="alert" aria-live="polite"></div>');
        }

        const ICONS = {
            success: '✅',
            danger:  '❌',
            warning: '⚠️',
            info:    'ℹ️',
            confetti:'🎉'
        };
        const BG = {
            success: 'bg-success',
            danger:  'bg-danger',
            warning: 'bg-warning text-dark',
            info:    'bg-primary',
            confetti:'bg-success toast-confetti'
        };

        const icon = ICONS[type] || ICONS.info;
        const bg   = BG[type]   || BG.info;

        const id = 'toast-' + Date.now();
        $('#toast-container').append(`
            <div id="${id}" class="toast align-items-center text-white ${bg} border-0" role="alert" aria-atomic="true" data-bs-delay="3000">
                <div class="d-flex">
                    <div class="toast-body"><span class="me-1">${icon}</span>${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
                </div>
            </div>`);
        new bootstrap.Toast(document.getElementById(id)).show();
        document.getElementById(id).addEventListener('hidden.bs.toast', function() { $(this).remove(); });
    }

    // =============================================
    // Socket.IO
    // =============================================
    if (typeof io !== 'undefined') {
        const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

        socket.on('nueva_orden_cocina', function(data) {
            showToast(`Orden #${data.orden_id} enviada a cocina.`, 'info');
        });

        socket.on('item_listo_notificacion', function(data) {
            showToast(`¡${data.producto_nombre} de orden #${data.orden_id} listo!`, 'success');
            var row = $('#product-item-' + data.item_id);
            if (row.length) {
                row.find('.estado-producto-texto').html('<span class="badge bg-success">Listo</span>');
                row.find('.accion-producto').html(
                    `<button class="btn btn-sm btn-primary btn-entregar-item"
                             data-detalle-id="${data.item_id}" data-orden-id="${data.orden_id}">Entregar</button>`
                );
                row.removeClass('detalle-pendiente-cocina detalle-entregado').addClass('detalle-listo-cocina');
                verificarEstadoParaCobro(data.orden_id);
            }
        });

        socket.on('orden_completa_lista', function(data) {
            showToast(`¡Orden #${data.orden_id} lista en cocina!`, 'success');
        });

        socket.on('orden_actualizada_para_cobro', function(data) {
            if (data.estado_orden === 'completada') {
                showToast(`Orden #${data.orden_id} lista para cobro.`, 'info');
                verificarEstadoParaCobro(data.orden_id);
            }
        });
    }

    // =============================================
    // Entregar item
    // =============================================
    $(document).on('click', '.btn-entregar-item', function(e) {
        e.stopPropagation();
        var detalleId = $(this).data('detalle-id');
        var ordenId = $(this).data('orden-id');
        if (!detalleId || !ordenId) return;

        $.ajax({
            type: 'POST',
            url: `/meseros/entregar_item/${ordenId}/${detalleId}`,
            success: function(res) {
                if (res.success) {
                    showToast(res.message, 'success');
                    var row = $('#product-item-' + detalleId);
                    row.find('.estado-producto-texto').html('<span class="badge bg-secondary">Entregado</span>');
                    row.find('.accion-producto').html('<span class="text-success fw-bold">Entregado <i class="fas fa-check"></i></span>');
                    row.removeClass('detalle-listo-cocina').addClass('detalle-entregado');
                    verificarEstadoParaCobro(ordenId);
                } else {
                    alert(res.message);
                }
            },
            error: function(xhr) {
                alert(xhr.responseJSON?.message || 'Error al entregar.');
            }
        });
    });

    // =============================================
    // Verificar estado para cobro
    // =============================================
    window.verificarEstadoParaCobro = function(ordenId) {
        var el = $('#orden-acordeon-' + ordenId);
        if (!el.length) return;
        var todos = true;
        var items = el.find('.product-row .estado-producto-texto');
        if (!items.length) { todos = false; }
        else {
            items.each(function() {
                if ($(this).text().trim().toLowerCase() !== 'entregado') {
                    todos = false; return false;
                }
            });
        }
        var btn = el.find('.btn-cobrar-orden');
        if (btn.length) {
            btn.prop('disabled', !todos)
               .toggleClass('btn-success', todos)
               .toggleClass('btn-outline-secondary disabled', !todos);
        }
    };

    // =============================================
    // Mostrar modal de cobro (con IVA, descuentos, multi-pago)
    // =============================================
    window.mostrarCobro = async function(ordenId) {
        const body = $('#modalCobroBody');
        const el = document.getElementById('modalCobro');
        if (!body.length || !el) return;

        body.html('<div class="text-center py-3"><div class="spinner-border"></div></div>');
        (bootstrap.Modal.getInstance(el) || new bootstrap.Modal(el)).show();

        try {
            const res = await fetch(`/meseros/ordenes/${ordenId}/cobrar_info`);
            if (!res.ok) throw new Error('Error cargando datos');
            const data = await res.json();

            let html = `
                <div class="text-center mb-2">
                    <img src="/static/img/logoCasaLeones.svg" alt="Logo" style="max-height:40px;">
                </div>
                <h5>Orden #${data.orden_id}${data.mesa_numero ? ' — Mesa ' + data.mesa_numero : ' — Para Llevar'}</h5>
                <hr>
                <table class="table table-sm">
                    <thead><tr><th>Producto</th><th class="text-center">Cant</th><th class="text-end">Precio</th><th class="text-end">Subtotal</th></tr></thead>
                    <tbody>`;

            data.detalles.forEach(item => {
                html += `<tr>
                    <td>${item.nombre}</td>
                    <td class="text-center">${item.cantidad}</td>
                    <td class="text-end">$${item.precio.toFixed(2)}</td>
                    <td class="text-end">$${item.subtotal.toFixed(2)}</td>
                </tr>`;
            });

            html += `</tbody></table>
                <div class="border-top pt-2">
                    <div class="d-flex justify-content-between"><span>Subtotal</span><span>$${data.subtotal.toFixed(2)}</span></div>`;

            if (data.descuento_pct > 0) {
                html += `<div class="d-flex justify-content-between text-danger"><span>Descuento (${data.descuento_pct}%)</span><span>-</span></div>`;
            }
            if (data.descuento_monto > 0) {
                html += `<div class="d-flex justify-content-between text-danger"><span>Descuento fijo</span><span>-$${data.descuento_monto.toFixed(2)}</span></div>`;
            }

            html += `
                    <div class="d-flex justify-content-between"><span>IVA (${data.iva_rate}%)</span><span>$${data.iva.toFixed(2)}</span></div>
                    <div class="d-flex justify-content-between fw-bold fs-5 mt-1"><span>Total</span><span>$${data.total.toFixed(2)}</span></div>
                </div>`;

            // Pagos previos (split)
            if (data.pagos.length > 0) {
                html += `<hr><h6>Pagos registrados</h6><ul class="list-group list-group-flush mb-2">`;
                data.pagos.forEach(p => {
                    html += `<li class="list-group-item d-flex justify-content-between">
                        <span>${p.metodo}${p.referencia ? ' ('+p.referencia+')' : ''}</span>
                        <span>$${p.monto.toFixed(2)}</span>
                    </li>`;
                });
                html += `</ul>
                    <div class="d-flex justify-content-between fw-bold">
                        <span>Pagado</span><span>$${data.total_pagado.toFixed(2)}</span>
                    </div>
                    <div class="d-flex justify-content-between fw-bold text-primary">
                        <span>Saldo pendiente</span><span>$${data.saldo_pendiente.toFixed(2)}</span>
                    </div>`;
            }

            if (data.saldo_pendiente <= 0 && data.pagos.length > 0) {
                html += `<div class="alert alert-success mt-3 text-center">Orden completamente pagada.</div>`;
            } else {
                html += `
                <hr>
                <h6>Propina</h6>
                <div class="btn-group w-100 mb-2" role="group" aria-label="Propina rápida">
                    <button type="button" class="btn btn-outline-secondary btn-propina" data-pct="0" data-orden="${ordenId}">Sin</button>
                    <button type="button" class="btn btn-outline-secondary btn-propina" data-pct="10" data-orden="${ordenId}">10%</button>
                    <button type="button" class="btn btn-outline-secondary btn-propina" data-pct="15" data-orden="${ordenId}">15%</button>
                    <button type="button" class="btn btn-outline-secondary btn-propina" data-pct="20" data-orden="${ordenId}">20%</button>
                </div>
                <div class="mb-2">
                    <label class="form-label">Propina personalizada ($)</label>
                    <input type="number" step="0.01" min="0" id="propina_monto_${ordenId}" class="form-control" value="0" placeholder="0.00">
                </div>
                <hr>
                <h6>Registrar Pago</h6>
                <div class="mb-2">
                    <label class="form-label">Método de pago</label>
                    <select id="pago_metodo_${ordenId}" class="form-select">
                        <option value="efectivo">Efectivo</option>
                        <option value="tarjeta">Tarjeta</option>
                        <option value="transferencia">Transferencia</option>
                    </select>
                </div>
                <div class="mb-2" id="referencia_group_${ordenId}" style="display:none;">
                    <label class="form-label">Referencia (últimos 4 dígitos / folio)</label>
                    <input type="text" id="pago_referencia_${ordenId}" class="form-control" maxlength="20">
                </div>
                <div class="mb-3">
                    <label class="form-label">Monto</label>
                    <input type="number" step="0.01" id="pago_monto_${ordenId}" class="form-control"
                           value="${data.saldo_pendiente.toFixed(2)}" min="0.01">
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-success flex-grow-1 btn-registrar-pago" data-orden-id="${ordenId}">
                        <i class="fas fa-cash-register me-1"></i>Registrar Pago
                    </button>
                    <button class="btn btn-outline-info btn-aplicar-descuento" data-orden-id="${ordenId}">
                        <i class="fas fa-percent me-1"></i>Descuento
                    </button>
                </div>`;
            }

            html += `<div class="mt-2"><button class="btn btn-secondary btn-sm w-100 btn-imprimir-ticket" data-orden-id="${ordenId}"><i class="fas fa-print me-1"></i>Imprimir Ticket</button></div>`;

            body.html(html);

            // Toggle referencia field
            $(`#pago_metodo_${ordenId}`).on('change', function() {
                $(`#referencia_group_${ordenId}`).toggle($(this).val() !== 'efectivo');
            });

            // Registrar pago handler
            body.find('.btn-registrar-pago').on('click', function() { registrarPago(ordenId); });

            // Descuento handler
            body.find('.btn-aplicar-descuento').on('click', function() { mostrarFormDescuento(ordenId); });

            // Print handler
            body.find('.btn-imprimir-ticket').on('click', function() { imprimirTicket(ordenId); });

            // Propina percentage buttons
            body.find('.btn-propina').on('click', function() {
                body.find('.btn-propina').removeClass('active btn-secondary').addClass('btn-outline-secondary');
                $(this).removeClass('btn-outline-secondary').addClass('active btn-secondary');
                const pct = parseFloat($(this).data('pct'));
                const propinaVal = (data.total * pct / 100);
                $(`#propina_monto_${ordenId}`).val(propinaVal.toFixed(2));
            });

        } catch (err) {
            body.html(`<p class="text-danger">Error: ${err.message}</p>`);
        }
    };

    // =============================================
    // Registrar pago (multi-método / split)
    // =============================================
    async function registrarPago(ordenId) {
        const metodo = $(`#pago_metodo_${ordenId}`).val();
        const monto = parseFloat($(`#pago_monto_${ordenId}`).val());
        const referencia = $(`#pago_referencia_${ordenId}`).val() || '';
        const propina = parseFloat($(`#propina_monto_${ordenId}`).val()) || 0;

        if (isNaN(monto) || monto <= 0) {
            alert('Ingresa un monto válido.'); return;
        }

        try {
            const res = await fetch(`/meseros/ordenes/${ordenId}/pago`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ metodo, monto, referencia, propina }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.message);

            if (data.orden_pagada) {
                const modalEl = document.getElementById('modalCobro');
                const inst = bootstrap.Modal.getInstance(modalEl);
                if (inst) inst.hide();
                let cambioMsg = data.cambio > 0 ? ` Cambio: $${data.cambio.toFixed(2)}` : '';
                showToast(`Orden #${ordenId} pagada.${cambioMsg}`, 'confetti');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast(`Pago de $${data.monto.toFixed(2)} (${metodo}) registrado. Saldo: $${data.saldo_pendiente.toFixed(2)}`, 'info');
                // Refresh modal
                mostrarCobro(ordenId);
            }
        } catch (err) {
            alert(err.message);
        }
    }

    // =============================================
    // Formulario de descuento (con autorización)
    // =============================================
    function mostrarFormDescuento(ordenId) {
        const body = $('#modalCobroBody');
        const prev = body.html();
        body.html(`
            <h5>Aplicar Descuento — Orden #${ordenId}</h5>
            <hr>
            <div class="mb-2">
                <label class="form-label">Tipo</label>
                <select id="desc_tipo" class="form-select">
                    <option value="porcentaje">Porcentaje (%)</option>
                    <option value="monto">Monto fijo ($)</option>
                </select>
            </div>
            <div class="mb-2">
                <label class="form-label">Valor</label>
                <input type="number" step="0.01" id="desc_valor" class="form-control" min="0" placeholder="Ej: 10">
            </div>
            <div class="mb-2">
                <label class="form-label">Motivo</label>
                <input type="text" id="desc_motivo" class="form-control" placeholder="Cortesía, error de cocina...">
            </div>
            <hr>
            <h6>Autorización (Admin/Superadmin)</h6>
            <div class="mb-2">
                <label class="form-label">Email autorizador</label>
                <input type="email" id="desc_auth_email" class="form-control">
            </div>
            <div class="mb-3">
                <label class="form-label">Contraseña</label>
                <input type="password" id="desc_auth_pass" class="form-control">
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-success flex-grow-1" id="btnConfirmarDesc">Confirmar Descuento</button>
                <button class="btn btn-secondary" id="btnCancelarDesc">Cancelar</button>
            </div>
        `);

        $('#btnCancelarDesc').on('click', function() { mostrarCobro(ordenId); });
        $('#btnConfirmarDesc').on('click', async function() {
            try {
                const res = await fetch(`/meseros/ordenes/${ordenId}/descuento`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tipo: $('#desc_tipo').val(),
                        valor: parseFloat($('#desc_valor').val()) || 0,
                        motivo: $('#desc_motivo').val(),
                        auth_email: $('#desc_auth_email').val(),
                        auth_password: $('#desc_auth_pass').val(),
                    }),
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.message);
                showToast('Descuento aplicado.', 'success');
                mostrarCobro(ordenId);
            } catch (err) {
                alert(err.message);
            }
        });
    }

    // =============================================
    // Imprimir ticket (Item 10)
    // =============================================
    window.imprimirTicket = async function(ordenId) {
        try {
            const res = await fetch(`/meseros/ordenes/${ordenId}/cobrar_info`);
            if (!res.ok) throw new Error('No se pudieron cargar los datos');
            const data = await res.json();

            const win = window.open('', '_blank', 'width=350,height=600');
            let html = `<!DOCTYPE html><html><head><meta charset="utf-8">
                <title>Ticket #${data.orden_id}</title>
                <style>
                    body{font-family:'Courier New',monospace;font-size:12px;width:280px;margin:0 auto;padding:10px;}
                    .center{text-align:center;}
                    .bold{font-weight:bold;}
                    .line{border-top:1px dashed #000;margin:5px 0;}
                    table{width:100%;border-collapse:collapse;}
                    td{padding:2px 0;}
                    .right{text-align:right;}
                    .total-row td{font-weight:bold;font-size:14px;padding-top:5px;}
                    @media print{body{margin:0;padding:5px;}}
                </style></head><body>
                <div class="center bold" style="font-size:16px;">CASA LEONES</div>
                <div class="center">Ticket de Venta</div>
                <div class="line"></div>
                <div>Orden: #${data.orden_id}</div>
                <div>${data.mesa_numero ? 'Mesa: ' + data.mesa_numero : 'Para Llevar'}</div>
                <div>Fecha: ${new Date().toLocaleString('es-MX')}</div>
                <div class="line"></div>
                <table>
                    <tr class="bold"><td>Producto</td><td class="right">Cant</td><td class="right">P.U.</td><td class="right">Importe</td></tr>`;

            data.detalles.forEach(item => {
                html += `<tr><td>${item.nombre}</td><td class="right">${item.cantidad}</td><td class="right">$${item.precio.toFixed(2)}</td><td class="right">$${item.subtotal.toFixed(2)}</td></tr>`;
            });

            html += `</table>
                <div class="line"></div>
                <table>
                    <tr><td>Subtotal</td><td class="right">$${data.subtotal.toFixed(2)}</td></tr>`;

            if (data.descuento_pct > 0) {
                html += `<tr><td>Descuento (${data.descuento_pct}%)</td><td class="right">-</td></tr>`;
            }
            if (data.descuento_monto > 0) {
                html += `<tr><td>Descuento</td><td class="right">-$${data.descuento_monto.toFixed(2)}</td></tr>`;
            }

            html += `<tr><td>IVA (${data.iva_rate}%)</td><td class="right">$${data.iva.toFixed(2)}</td></tr>
                    <tr class="total-row"><td>TOTAL</td><td class="right">$${data.total.toFixed(2)}</td></tr>
                </table>`;

            if (data.pagos.length > 0) {
                html += `<div class="line"></div><div class="bold">Pagos:</div>`;
                data.pagos.forEach(p => {
                    html += `<div>${p.metodo}: $${p.monto.toFixed(2)}${p.referencia ? ' ('+p.referencia+')' : ''}</div>`;
                });
            }

            html += `<div class="line"></div>
                <div class="center">¡Gracias por su visita!</div>
                <div class="center" style="font-size:10px;">Casa Leones POS v2.0</div>
                <script>window.onload=function(){window.print();}<\/script>
                </body></html>`;

            win.document.write(html);
            win.document.close();
        } catch (err) {
            alert('Error generando ticket: ' + err.message);
        }
    };

    // =============================================
    // Delegación botón cobrar
    // =============================================
    $(document).on('click', '.btn-cobrar-orden:not(:disabled)', function() {
        var ordenId = $(this).data('orden-id');
        if (ordenId) mostrarCobro(ordenId);
    });

    // Modal cleanup
    const modalCobroEl = document.getElementById('modalCobro');
    if (modalCobroEl) {
        modalCobroEl.addEventListener('hidden.bs.modal', () => {
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        });
    }

    // Verificar cobro al cargar
    $('.accordion-item[id^="orden-acordeon-"]').each(function() {
        var ordenId = $(this).attr('id').replace('orden-acordeon-', '');
        if (ordenId) verificarEstadoParaCobro(ordenId);
    });

});
