/**
 * Cocina Timers — KDS v6
 * Timer + urgency gradient for KDS cards.
 * Thresholds: 0-5min green, 5-10min yellow, 10-15min red, 15+ urgent pulse.
 * Exports window.initKdsTimers() for re-init after AJAX refresh.
 */
(function() {
    'use strict';

    const T_GREEN  = 300;   // 5 min
    const T_YELLOW = 600;   // 10 min
    const T_RED    = 900;   // 15 min

    function getUrgency(sec) {
        if (sec >= T_RED)    return 'urgent';
        if (sec >= T_YELLOW) return 'red';
        if (sec >= T_GREEN)  return 'yellow';
        return 'green';
    }

    function updateTimers() {
        document.querySelectorAll('.orden-timer-card').forEach(function(card) {
            const iso = card.getAttribute('data-tiempo-registro');
            if (!iso) return;

            const diffSec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
            const mins = Math.floor(diffSec / 60);
            const secs = diffSec % 60;
            const display = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');

            const badge = card.querySelector('.timer-badge');
            if (badge) {
                badge.textContent = display;
                // Timer badge color
                badge.className = 'kds-card__timer timer-badge kds-card__timer--' + getUrgency(diffSec);
            }

            // Card border color (for KDS cards)
            card.classList.remove('kds-card--green', 'kds-card--yellow', 'kds-card--red', 'kds-card--urgent');
            card.classList.add('kds-card--' + getUrgency(diffSec));

            // Legacy Bootstrap badge support (backward compat)
            if (badge && badge.classList.contains('bg-dark')) {
                badge.classList.remove('bg-dark', 'bg-success', 'bg-warning', 'bg-danger', 'text-dark');
                if (diffSec >= T_YELLOW) badge.classList.add('bg-danger');
                else if (diffSec >= T_GREEN) badge.classList.add('bg-warning', 'text-dark');
                else badge.classList.add('bg-success');
            }
        });
    }

    function init() {
        updateTimers();
    }

    // Expose for AJAX re-init
    window.initKdsTimers = init;

    // Run immediately and every second
    init();
    setInterval(updateTimers, 1000);
})();
