document.addEventListener('DOMContentLoaded', async () => {
    const [{ ventasHoy }, { ordenesHoy }, { ticketPromedio }, top] = await Promise.all([
      fetch('/api/dashboard/ventas_hoy').then(r => r.json()),
      fetch('/api/dashboard/ordenes_hoy').then(r => r.json()),
      fetch('/api/dashboard/ticket_promedio').then(r => r.json()),
      fetch('/api/dashboard/top_productos').then(r => r.json())
    ]);
    document.getElementById('ventasHoy').innerText = ventasHoy.toFixed(2);
    document.getElementById('ordenesHoy').innerText = ordenesHoy;
    document.getElementById('ticketPromedio').innerText = ticketPromedio.toFixed(2);
    // Inicializar gráfica
    const ctx = document.getElementById('chartTopProductos').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: { labels: top.labels, datasets: [{ label: 'Unidades', data: top.data }] },
      options: { scales: { y: { beginAtZero: true } } }
    });
  });