/**
 * Mapa Visual de Mesas — Sprint 4 (5.1)
 * Interactive map with Socket.IO real-time updates and drag-and-drop (admin).
 */
(function() {
  'use strict';

  const mapContainer = document.getElementById('mapa-mesas');
  if (!mapContainer) return;

  const isAdmin = mapContainer.dataset.admin === 'true';
  const mesasApiUrl = '/admin/reservaciones/api/mesas';
  const ordenBaseUrl = '/meseros/ordenes/';
  const crearOrdenUrl = '/meseros/seleccionar_mesa';

  let mesas = [];
  let dragTarget = null;
  let dragOffset = { x: 0, y: 0 };

  // ─── Load mesas ─────────────────────────────────────────────
  function fetchMesas() {
    fetch(mesasApiUrl)
      .then(r => r.json())
      .then(data => {
        mesas = data;
        renderMap();
        renderListView();
      })
      .catch(err => console.error('Error cargando mesas:', err));
  }

  // ─── Render SVG-like map ────────────────────────────────────
  function renderMap() {
    mapContainer.innerHTML = '';

    mesas.forEach(m => {
      const el = document.createElement('div');
      el.className = `mesa-item estado-${m.estado}`;
      el.dataset.mesaId = m.id;
      el.style.left = (m.pos_x || 20) + 'px';
      el.style.top = (m.pos_y || 20) + 'px';
      el.setAttribute('tabindex', '0');
      el.setAttribute('role', 'button');
      el.setAttribute('aria-label', `Mesa ${m.numero}, ${m.capacidad} personas, ${m.estado}${m.zona ? ', zona ' + m.zona : ''}`);

      el.innerHTML = `
        <span class="mesa-numero">${m.numero}</span>
        <span class="mesa-capacidad">${m.capacidad} pers.</span>
        ${m.zona ? `<span class="mesa-zona">${m.zona}</span>` : ''}
      `;

      el.addEventListener('click', () => handleMesaClick(m));
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleMesaClick(m);
        }
      });

      // Admin drag-and-drop
      if (isAdmin) {
        el.style.cursor = 'grab';
        el.addEventListener('mousedown', startDrag);
        el.addEventListener('touchstart', startDragTouch, { passive: false });
      }

      mapContainer.appendChild(el);
    });
  }

  // ─── List view for mobile ──────────────────────────────────
  function renderListView() {
    const listEl = document.getElementById('mapa-list-view');
    if (!listEl) return;

    listEl.innerHTML = '';
    mesas.forEach(m => {
      const row = document.createElement('a');
      row.href = '#';
      row.className = `list-group-item list-group-item-action d-flex justify-content-between align-items-center`;
      row.innerHTML = `
        <div>
          <strong>Mesa ${m.numero}</strong>
          <small class="text-muted ms-2">${m.zona || ''}</small>
        </div>
        <div>
          <span class="badge bg-${estadoBadge(m.estado)} me-2">${m.estado}</span>
          <small>${m.capacidad} pers.</small>
        </div>
      `;
      row.addEventListener('click', (e) => {
        e.preventDefault();
        handleMesaClick(m);
      });
      listEl.appendChild(row);
    });
  }

  function estadoBadge(estado) {
    const map = { disponible: 'success', ocupada: 'danger', reservada: 'warning', mantenimiento: 'secondary' };
    return map[estado] || 'secondary';
  }

  // ─── Click handler ─────────────────────────────────────────
  function handleMesaClick(mesa) {
    if (mesa.estado === 'disponible') {
      // Create order for this mesa — POST form
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = crearOrdenUrl;
      form.innerHTML = `<input type="hidden" name="csrf_token" value="${window.__csrfToken}">
                         <input type="hidden" name="mesa_id" value="${mesa.id}">`;
      document.body.appendChild(form);
      form.submit();
    } else if (mesa.estado === 'ocupada') {
      // Redirect to active order for this mesa
      fetch(`/api/ordenes/mesa/${mesa.id}`)
        .then(r => r.json())
        .then(data => {
          if (data.orden_id) {
            window.location.href = `${ordenBaseUrl}${data.orden_id}/detalle_orden`;
          } else {
            showMapToast(`Mesa ${mesa.numero} ocupada pero sin orden activa.`, 'warning');
          }
        })
        .catch(() => showMapToast('Error al buscar orden.', 'danger'));
    } else {
      showMapToast(`Mesa ${mesa.numero}: ${mesa.estado}`, 'info');
    }
  }

  // ─── Drag & Drop (admin) ───────────────────────────────────
  function startDrag(e) {
    if (!isAdmin) return;
    e.preventDefault();
    dragTarget = e.currentTarget;
    dragTarget.classList.add('dragging');
    const rect = dragTarget.getBoundingClientRect();
    const containerRect = mapContainer.getBoundingClientRect();
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;

    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', endDrag);
  }

  function startDragTouch(e) {
    if (!isAdmin) return;
    e.preventDefault();
    const touch = e.touches[0];
    dragTarget = e.currentTarget;
    dragTarget.classList.add('dragging');
    const rect = dragTarget.getBoundingClientRect();
    dragOffset.x = touch.clientX - rect.left;
    dragOffset.y = touch.clientY - rect.top;

    document.addEventListener('touchmove', onDragTouch, { passive: false });
    document.addEventListener('touchend', endDragTouch);
  }

  function onDrag(e) {
    if (!dragTarget) return;
    const containerRect = mapContainer.getBoundingClientRect();
    let x = e.clientX - containerRect.left - dragOffset.x;
    let y = e.clientY - containerRect.top - dragOffset.y;
    x = Math.max(0, Math.min(x, containerRect.width - 100));
    y = Math.max(0, Math.min(y, containerRect.height - 80));
    dragTarget.style.left = x + 'px';
    dragTarget.style.top = y + 'px';
  }

  function onDragTouch(e) {
    if (!dragTarget) return;
    e.preventDefault();
    const touch = e.touches[0];
    const containerRect = mapContainer.getBoundingClientRect();
    let x = touch.clientX - containerRect.left - dragOffset.x;
    let y = touch.clientY - containerRect.top - dragOffset.y;
    x = Math.max(0, Math.min(x, containerRect.width - 100));
    y = Math.max(0, Math.min(y, containerRect.height - 80));
    dragTarget.style.left = x + 'px';
    dragTarget.style.top = y + 'px';
  }

  function endDrag() {
    if (!dragTarget) return;
    dragTarget.classList.remove('dragging');
    saveMesaPosition(dragTarget);
    dragTarget = null;
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', endDrag);
  }

  function endDragTouch() {
    if (!dragTarget) return;
    dragTarget.classList.remove('dragging');
    saveMesaPosition(dragTarget);
    dragTarget = null;
    document.removeEventListener('touchmove', onDragTouch);
    document.removeEventListener('touchend', endDragTouch);
  }

  function saveMesaPosition(el) {
    const mesaId = el.dataset.mesaId;
    const posX = parseInt(el.style.left);
    const posY = parseInt(el.style.top);

    fetch(`/admin/mesas/${mesaId}/posicion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pos_x: posX, pos_y: posY }),
    })
    .then(r => r.json())
    .then(data => {
      if (!data.success) console.error('Error guardando posición');
    })
    .catch(err => console.error('Error:', err));
  }

  // ─── Toast helper ──────────────────────────────────────────
  function showMapToast(message, type) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const bg = { success: 'bg-success', danger: 'bg-danger', warning: 'bg-warning text-dark', info: 'bg-info' }[type] || 'bg-info';
    const id = 'toast-' + Date.now();
    container.insertAdjacentHTML('beforeend', `
      <div id="${id}" class="toast align-items-center text-white ${bg} border-0" role="alert" data-bs-delay="3000">
        <div class="d-flex">
          <div class="toast-body">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    `);
    new bootstrap.Toast(document.getElementById(id)).show();
    document.getElementById(id).addEventListener('hidden.bs.toast', function() { this.remove(); });
  }

  // ─── Zone filter ───────────────────────────────────────────
  document.querySelectorAll('[data-zone-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      const zone = btn.dataset.zoneFilter;
      document.querySelectorAll('[data-zone-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      document.querySelectorAll('.mesa-item').forEach(el => {
        const mesaId = el.dataset.mesaId;
        const mesa = mesas.find(m => String(m.id) === mesaId);
        if (!zone || zone === 'todas') {
          el.style.display = '';
        } else {
          el.style.display = (mesa && mesa.zona === zone) ? '' : 'none';
        }
      });
    });
  });

  // ─── Socket.IO real-time ───────────────────────────────────
  if (typeof io !== 'undefined') {
    const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('mesa_estado_actualizado', function(data) {
      const el = document.querySelector(`.mesa-item[data-mesa-id="${data.mesa_id}"]`);
      if (el) {
        el.className = `mesa-item estado-${data.estado}`;
        // Preserve position
        el.style.left = el.style.left;
        el.style.top = el.style.top;
      }
      // Update data
      const mesa = mesas.find(m => m.id === data.mesa_id);
      if (mesa) mesa.estado = data.estado;
      renderListView();
    });
  }

  // ─── Init ──────────────────────────────────────────────────
  fetchMesas();
  // Auto-refresh every 30s
  setInterval(fetchMesas, 30000);

})();
