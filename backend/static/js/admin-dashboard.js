/**
 * Admin Dashboard — Sprint 5 (5.4)
 * Fetches 9 API endpoints, renders 8 KPI widgets, 2 charts,
 * stock alerts, activity feed. Auto-refreshes every 30s.
 */
(function() {
  'use strict';

  const COLORS = {
    primary: '#A6192E',
    secondary: '#0A3D62',
    accent: '#507C36',
    warning: '#FFD6B0',
    dark: '#1E1E1E',
    light: '#FAF3E0',
  };
  const REFRESH_MS = 30000;
  let chart7Dias = null;
  let chartTop = null;

  // Currency formatter
  const currency = v => '$' + Number(v).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  // Fetch helper
  const api = endpoint => fetch(`/admin/api/dashboard/${endpoint}`).then(r => r.json());

  // Estado badge helper
  function estadoBadge(estado) {
    const map = {
      pendiente: 'bg-warning text-dark',
      en_preparacion: 'bg-info text-dark',
      completada: 'bg-success',
      pagado: 'bg-primary',
      cancelada: 'bg-danger',
    };
    return `<span class="badge ${map[estado] || 'bg-secondary'}">${estado}</span>`;
  }

  // ---- KPI Updates ----
  async function refreshKPIs() {
    try {
      const [ventas, ordenes, ticket, propinas, mesas, cocina, stock, corte] = await Promise.all([
        api('ventas_hoy'),
        api('ordenes_hoy'),
        api('ticket_promedio'),
        api('propinas_hoy'),
        api('mesas_activas'),
        api('ordenes_cocina'),
        api('alertas_stock'),
        api('ultimo_corte'),
      ]);

      document.getElementById('ventasHoy').textContent = currency(ventas.ventasHoy);
      document.getElementById('ordenesHoy').textContent = ordenes.ordenesHoy;
      document.getElementById('ticketPromedio').textContent = currency(ticket.ticketPromedio);
      document.getElementById('propinasHoy').textContent = currency(propinas.propinas);

      // Mesas
      document.getElementById('mesasActivas').textContent = `${mesas.ocupadas}/${mesas.total}`;
      document.getElementById('mesasReservadas').textContent = mesas.reservadas > 0 ? `${mesas.reservadas} reservada(s)` : '';

      // Cocina
      document.getElementById('ordenesCocina').textContent = cocina.pendientes;
      document.getElementById('timerCocina').textContent = cocina.timer_promedio_min > 0
        ? `~${cocina.timer_promedio_min} min promedio`
        : 'Sin órdenes activas';

      // Stock alerts count
      const countEl = document.getElementById('alertasStockCount');
      countEl.textContent = stock.count;
      if (stock.count > 0) {
        countEl.classList.add('text-danger');
      } else {
        countEl.classList.remove('text-danger');
      }

      // Stock alerts list
      const stockList = document.getElementById('stockAlertsList');
      if (stock.count === 0) {
        stockList.innerHTML = '<p class="text-muted text-center mb-0">Sin alertas de inventario 👍</p>';
      } else {
        stockList.innerHTML = stock.items.map(item => {
          const pct = item.minimo > 0 ? Math.min((item.stock / item.minimo) * 100, 100) : 0;
          const color = pct < 30 ? '#dc3545' : pct < 70 ? '#ffc107' : '#28a745';
          return `
            <div class="stock-alert-item d-flex justify-content-between align-items-center mb-2">
              <div>
                <strong>${item.nombre}</strong>
                <div class="stock-bar mt-1" style="width:100px;">
                  <div class="stock-bar-fill" style="width:${pct}%; background:${color};"></div>
                </div>
              </div>
              <span class="text-end">${item.stock} / ${item.minimo} ${item.unidad}</span>
            </div>`;
        }).join('');
      }

      // Último corte
      const corteEl = document.getElementById('ultimoCorteInfo');
      if (!corte.exists) {
        corteEl.innerHTML = '<div class="kpi-value">—</div><small class="text-muted">Sin cortes registrados</small>';
      } else {
        const diffClass = corte.diferencia >= 0 ? 'text-success' : 'text-danger';
        const diffSign = corte.diferencia >= 0 ? '+' : '';
        corteEl.innerHTML = `
          <div class="kpi-value" style="font-size:1.2rem;">${currency(corte.total_ingresos)}</div>
          <small class="text-muted">${corte.fecha} · ${corte.usuario}</small><br>
          <small class="${diffClass} fw-bold">Dif: ${diffSign}${currency(corte.diferencia)}</small>`;
      }

    } catch (err) {
      console.error('Error refreshing KPIs:', err);
    }
  }

  // ---- Charts ----
  async function refreshCharts() {
    try {
      const [ventas7, top] = await Promise.all([
        api('ventas_7dias'),
        api('top_productos'),
      ]);

      // 7-day sales line chart
      const ctx7 = document.getElementById('chart7Dias');
      if (chart7Dias) {
        chart7Dias.data.labels = ventas7.labels;
        chart7Dias.data.datasets[0].data = ventas7.data;
        chart7Dias.update();
      } else {
        chart7Dias = new Chart(ctx7, {
          type: 'line',
          data: {
            labels: ventas7.labels,
            datasets: [{
              label: 'Ventas ($)',
              data: ventas7.data,
              borderColor: COLORS.primary,
              backgroundColor: COLORS.primary + '30',
              fill: true,
              tension: 0.3,
              pointRadius: 5,
              pointBackgroundColor: COLORS.primary,
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false },
              tooltip: { callbacks: { label: ctx => currency(ctx.parsed.y) } },
            },
            scales: {
              y: { beginAtZero: true, ticks: { callback: v => '$' + v.toLocaleString('es-MX') } }
            }
          }
        });
      }

      // Top products bar chart
      const ctxTop = document.getElementById('chartTopProductos');
      if (chartTop) {
        chartTop.data.labels = top.labels;
        chartTop.data.datasets[0].data = top.data;
        chartTop.update();
      } else {
        chartTop = new Chart(ctxTop, {
          type: 'bar',
          data: {
            labels: top.labels,
            datasets: [{
              label: 'Unidades',
              data: top.data,
              backgroundColor: [COLORS.primary, COLORS.secondary, COLORS.accent, '#c29e59', '#666'],
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } }
          }
        });
      }
    } catch (err) {
      console.error('Error refreshing charts:', err);
    }
  }

  // ---- Activity Feed ----
  async function refreshActivity() {
    try {
      const data = await api('actividad_reciente');
      const feed = document.getElementById('activityFeed');
      if (!data.items.length) {
        feed.innerHTML = '<p class="text-muted text-center">Sin actividad reciente.</p>';
        return;
      }
      feed.innerHTML = data.items.map(item => `
        <div class="activity-item mb-2 py-1">
          <div class="d-flex justify-content-between">
            <span><strong>Orden #${item.id}</strong> · Mesa ${item.mesa} · ${item.mesero}</span>
            <span class="text-muted">${item.hora}</span>
          </div>
          <div class="d-flex justify-content-between">
            ${estadoBadge(item.estado)}
            <span class="fw-bold">${item.total > 0 ? currency(item.total) : '—'}</span>
          </div>
        </div>`).join('');
    } catch (err) {
      console.error('Error refreshing activity:', err);
    }
  }

  // ---- Auto-refresh ----
  function refreshAll() {
    refreshKPIs();
    refreshCharts();
    refreshActivity();
  }

  document.addEventListener('DOMContentLoaded', () => {
    refreshAll();
    setInterval(refreshAll, REFRESH_MS);
  });

})();