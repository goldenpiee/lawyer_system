document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    let currentMonth = today.getMonth();
    let currentYear = today.getFullYear();
    let selectedDays = new Set();

    function updateSelectedDatesDisplay() {
        const display = document.getElementById('selectedDatesDisplay');
        if (!display) return;

        if (selectedDays.size === 0) {
            display.innerHTML = '<em class="text-muted small">Нет выбранных дней</em>';
        } else {
            const datesArray = Array.from(selectedDays);
            datesArray.sort((a, b) => new Date(a) - new Date(b));
            display.innerHTML = datesArray.map(dateStr => {
                const date = new Date(dateStr + 'T00:00:00');
                return `<span class="badge bg-primary me-1 mb-1">${date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })}</span>`;
            }).join('');
        }
        const input = document.getElementById('selectedDatesInput');
        if (input) input.value = Array.from(selectedDays).join(',');
    }

    function renderCalendar(month, year) {
        const calendarDaysEl = document.getElementById('calendar-days');
        if (!calendarDaysEl) return;

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        const todayDate = new Date();
        const todayDateZero = new Date(todayDate);
        todayDateZero.setHours(0, 0, 0, 0);

        let html = `<div class="calendar-header d-flex justify-content-between align-items-center mb-2">`;
        html += `<button type="button" class="btn btn-outline-secondary btn-sm" id="prevMonthBtn">«</button>`;
        html += `<h5 class="mb-0 mx-2">${firstDay.toLocaleString('ru-RU', {month: 'long', year: 'numeric'})}</h5>`;
        html += `<button type="button" class="btn btn-outline-secondary btn-sm" id="nextMonthBtn">»</button>`;
        html += `</div>`;

        html += '<div class="row g-0 text-center mb-1 calendar-days-header">';
        ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'].forEach(d => {
            html += `<div class="col"><small class="text-muted fw-bold">${d}</small></div>`;
        });
        html += '</div>';

        html += '<div class="row g-0">';

        let dayOfWeek = (firstDay.getDay() + 6) % 7;
        for (let i = 0; i < dayOfWeek; i++) {
            html += '<div class="col"><div class="p-1"></div></div>';
        }

        for (let day = 1; day <= lastDay.getDate(); day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const date = new Date(year, month, day);
            date.setHours(0, 0, 0, 0);
            const isSelected = selectedDays.has(dateStr);
            const isPast = date.getTime() < todayDateZero.getTime();

            if ((dayOfWeek + day - 1) % 7 === 0 && day !== 1) {
                html += '</div><div class="row g-0">';
            }

            html += `<div class="col">
                <div class="calendar-day-selectable ${isSelected ? 'selected' : ''} ${isPast ? 'disabled' : ''}"
                    data-date="${dateStr}" ${isPast ? 'aria-disabled="true"' : ''}>
                    ${day}
                </div>
            </div>`;
        }

        const remainingCells = 7 - ((dayOfWeek + lastDay.getDate()) % 7);
        if (remainingCells < 7) {
            for (let i = 0; i < remainingCells; i++) {
                html += '<div class="col"><div class="p-1"></div></div>';
            }
        }

        html += '</div>';
        calendarDaysEl.innerHTML = html;

        const prevBtn = document.getElementById('prevMonthBtn');
        const nextBtn = document.getElementById('nextMonthBtn');

        if (prevBtn) {
            const prevMonthDate = new Date(year, month - 1, 1);
            const isPrevMonthInPast = prevMonthDate.getFullYear() < today.getFullYear() ||
                (prevMonthDate.getFullYear() === today.getFullYear() && prevMonthDate.getMonth() < today.getMonth());
            prevBtn.disabled = isPrevMonthInPast;
            prevBtn.onclick = () => {
                if (currentMonth === 0) { currentMonth = 11; currentYear--; }
                else { currentMonth--; }
                renderCalendar(currentMonth, currentYear);
            };
        }

        if (nextBtn) {
            nextBtn.onclick = () => {
                if (currentMonth === 11) { currentMonth = 0; currentYear++; }
                else { currentMonth++; }
                renderCalendar(currentMonth, currentYear);
            };
        }

        calendarDaysEl.querySelectorAll('.calendar-day-selectable:not(.disabled)').forEach(el => {
            el.onclick = function() {
                const date = this.dataset.date;
                if (selectedDays.has(date)) {
                    selectedDays.delete(date);
                    this.classList.remove('selected');
                } else {
                    selectedDays.add(date);
                    this.classList.add('selected');
                }
                updateSelectedDatesDisplay();
            };
        });
    }

    const form = document.getElementById('generateSlotsForm');
    if (form) {
        form.onsubmit = function(e) {
            if (selectedDays.size === 0) {
                e.preventDefault();
                if (typeof showTemporaryMessage === 'function') {
                    showTemporaryMessage('Пожалуйста, выберите хотя бы один день', 'warning');
                } else {
                    alert('Пожалуйста, выберите хотя бы один день');
                }
                return false;
            }
        };
    }

    renderCalendar(currentMonth, currentYear);
    updateSelectedDatesDisplay();
});