/**
 * Cocina Timers — Fase 2 Item 11
 * Muestra tiempo transcurrido en cada orden de cocina.
 * Color coding: verde < 10 min, amarillo 10-20 min, rojo > 20 min.
 */
(function() {
    'use strict';

    const WARN_SECONDS = 600;   // 10 min → amarillo
    const DANGER_SECONDS = 1200; // 20 min → rojo

    function updateTimers() {
        document.querySelectorAll('.orden-timer-card').forEach(function(card) {
            const iso = card.getAttribute('data-tiempo-registro');
            if (!iso) return;

            const created = new Date(iso);
            const now = new Date();
            const diffSec = Math.floor((now - created) / 1000);

            const mins = Math.floor(diffSec / 60);
            const secs = diffSec % 60;
            const display = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');

            const badge = card.querySelector('.timer-badge');
            if (!badge) return;

            badge.textContent = display;

            // Color coding
            badge.classList.remove('bg-dark', 'bg-success', 'bg-warning', 'bg-danger', 'text-dark');
            if (diffSec >= DANGER_SECONDS) {
                badge.classList.add('bg-danger');
                // Pulse animation for urgency
                if (!card.classList.contains('timer-urgent')) {
                    card.classList.add('timer-urgent');
                }
            } else if (diffSec >= WARN_SECONDS) {
                badge.classList.add('bg-warning', 'text-dark');
                card.classList.remove('timer-urgent');
            } else {
                badge.classList.add('bg-success');
                card.classList.remove('timer-urgent');
            }
        });
    }

    // Run immediately and every second
    updateTimers();
    setInterval(updateTimers, 1000);
})();
