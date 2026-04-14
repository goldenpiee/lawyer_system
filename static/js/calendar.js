document.addEventListener('DOMContentLoaded', function() {
    let currentDate = new Date(window.initialDateStr || new Date());
    currentDate.setDate(1); 
    let slotsData = window.slotsData || [];
    
    window.selectedSlotId = null;
    window.selectedDateForSlot = null; 

    const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
    const csrfToken = window.csrfToken || document.querySelector('[name=csrfmiddlewaretoken]').value;

    const els = {
        monthHeader: document.getElementById('month-header'),
        calendarGrid: document.getElementById('calendar-grid'),
        timeSlots: document.getElementById('time-slots'),
        selectedDateHeader: document.getElementById('selected-date'),
        chooseTimeLabel: document.getElementById('choose-time-label'),
        slotList: document.getElementById('slot-list'),
        confirmBtn: document.getElementById('confirm-btn'),
        addTimeBtn: document.getElementById('add-time-btn'),
        createSlotForm: document.getElementById('createSlotForm'),
        selectedDateDisplay: document.getElementById('selectedDateDisplay'),
        slotStartTimeSelect: document.getElementById('slotStartTime'),
        deleteAllSlotsBtn: document.getElementById('deleteAllSlotsBtn'),
        confirmDeleteModal: document.getElementById('confirmDeleteModal'),
        confirmDeleteBtn: document.getElementById('confirmDeleteBtn'),
        deleteCountdown: document.getElementById('deleteCountdown')
    };

    function initCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const lastDayOfMonth = new Date(year, month + 1, 0);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (els.monthHeader) els.monthHeader.textContent = `${monthNames[month]} ${year}`;

        if (els.calendarGrid) {
            els.calendarGrid.innerHTML = '';
            let currentRow = document.createElement('div');
            currentRow.className = 'row row-cols-7 g-2';
            els.calendarGrid.appendChild(currentRow);

            let dayOfWeekCounter = 0;
            const startDayIndex = (new Date(year, month, 1).getDay() + 6) % 7;

            for (let i = 0; i < startDayIndex; i++) {
                const col = document.createElement('div');
                col.className = 'col p-0';
                const dayDiv = document.createElement('div');
                dayDiv.className = 'calendar-day empty';
                col.appendChild(dayDiv);
                currentRow.appendChild(col);
                dayOfWeekCounter++;
            }

            for (let day = 1; day <= lastDayOfMonth.getDate(); day++) {
                const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                const currentDayDate = new Date(year, month, day);
                const isPast = currentDayDate.getTime() < today.getTime();

                const hasAvailableSlots = slotsData.some(s => {
                    const slotDate = new Date(s.fields.start_time);
                    const sDate = `${slotDate.getFullYear()}-${String(slotDate.getMonth()+1).padStart(2,'0')}-${String(slotDate.getDate()).padStart(2,'0')}`;
                    return sDate === dateString && !s.fields.is_booked;
                });

                const col = document.createElement('div');
                col.className = 'col p-0';
                const dayDiv = document.createElement('div');

                let dayClasses = ['calendar-day'];
                if (isPast) dayClasses.push('past-day');
                else if (hasAvailableSlots) dayClasses.push('available-day');
                else dayClasses.push('no-slots-day');

                if (currentDayDate.getTime() === today.getTime()) dayClasses.push('today');

                dayDiv.className = dayClasses.join(' ');
                dayDiv.dataset.date = dateString;

                if (!isPast) {
                    dayDiv.addEventListener('click', function() {
                        showTimeSlots(dateString, this);
                    });
                }

                const span = document.createElement('span');
                span.textContent = day;
                dayDiv.appendChild(span);

                if (hasAvailableSlots) {
                    const indicator = document.createElement('div');
                    indicator.className = 'slot-indicator';
                    dayDiv.appendChild(indicator);
                }

                col.appendChild(dayDiv);
                currentRow.appendChild(col);
                dayOfWeekCounter++;
                
                if (dayOfWeekCounter % 7 === 0 && day < lastDayOfMonth.getDate()) {
                    currentRow = document.createElement('div');
                    currentRow.className = 'row row-cols-7 g-2';
                    els.calendarGrid.appendChild(currentRow);
                }
            }

            while (dayOfWeekCounter % 7 !== 0) {
                const col = document.createElement('div');
                col.className = 'col p-0';
                const dayDiv = document.createElement('div');
                dayDiv.className = 'calendar-day empty';
                col.appendChild(dayDiv);
                currentRow.appendChild(col);
                dayOfWeekCounter++;
            }
        }

        if (els.timeSlots) els.timeSlots.classList.add('d-none');
        if (els.createSlotForm) els.createSlotForm.classList.add('d-none');
    }

    async function loadSlots(year, month) {
        try {
            const response = await fetch(`/appointments/slots/?year=${year}&month=${month}`, {
                headers: { 'X-CSRFToken': csrfToken, 'Accept': 'application/json' }
            });
            const data = await response.json();
            slotsData = JSON.parse(data.slots);
            initCalendar();
        } catch (error) {
            console.error(error);
            if (els.calendarGrid) els.calendarGrid.innerHTML = '<div class="alert alert-danger">Ошибка загрузки календаря.</div>';
        }
    }

    window.changeMonth = function(offset) {
        currentDate.setMonth(currentDate.getMonth() + offset);
        loadSlots(currentDate.getFullYear(), currentDate.getMonth() + 1);
    }

    window.showTimeSlots = function(dateString, element) { 
        if (!element || element.classList.contains('past-day')) return;
        window.selectedDateForSlot = dateString; 

        document.querySelectorAll('.calendar-day.selected-day').forEach(d => d.classList.remove('selected-day'));
        element.classList.add('selected-day');

        const filteredSlots = slotsData.filter(s => {
            const slotDate = new Date(s.fields.start_time);
            const sDate = `${slotDate.getFullYear()}-${String(slotDate.getMonth()+1).padStart(2,'0')}-${String(slotDate.getDate()).padStart(2,'0')}`;
            return sDate === dateString && !s.fields.is_booked;
        }).sort((a, b) => new Date(a.fields.start_time) - new Date(b.fields.start_time));

        if (els.slotList) els.slotList.innerHTML = '';
        
        if (filteredSlots.length > 0) {
            const timeGroups = {};
            filteredSlots.forEach(s => {
                const hour = new Date(s.fields.start_time).getHours();
                if (!timeGroups[hour]) timeGroups[hour] = [];
                timeGroups[hour].push(s);
            });
            
            Object.entries(timeGroups).forEach(([hour, slots]) => {
                const groupDiv = document.createElement('div');
                groupDiv.className = 'time-group mb-2';

                const headerDiv = document.createElement('div');
                headerDiv.className = 'time-header';
                headerDiv.textContent = `${String(hour).padStart(2, '0')}:00`;
                groupDiv.appendChild(headerDiv);

                const gridDiv = document.createElement('div');
                gridDiv.className = 'time-slots-grid';

                slots.forEach(s => {
                    const btn = document.createElement('button');
                    btn.className = 'time-slot-btn';
                    btn.textContent = new Date(s.fields.start_time).toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'});
                    btn.addEventListener('click', function() {
                        selectSlot(s.pk, this);
                    });
                    gridDiv.appendChild(btn);
                });

                groupDiv.appendChild(gridDiv);
                if (els.slotList) els.slotList.appendChild(groupDiv);
            });
            
            if (els.chooseTimeLabel) els.chooseTimeLabel.classList.remove('d-none');
        } else {
            const p = document.createElement('p');
            p.className = 'text-muted text-center my-3';
            p.textContent = 'На этот день нет доступного времени.';
            if (els.slotList) els.slotList.appendChild(p);
            if (els.chooseTimeLabel) els.chooseTimeLabel.classList.add('d-none');
        }

        const dateObj = new Date(dateString);
        if (els.selectedDateHeader) els.selectedDateHeader.textContent = dateObj.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', weekday: 'long' });
        
        if (els.timeSlots) {
            els.timeSlots.classList.remove('d-none');
            els.timeSlots.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        if (els.confirmBtn) els.confirmBtn.classList.add('d-none');
        if (els.addTimeBtn) els.addTimeBtn.style.display = 'block';
        if (els.createSlotForm) els.createSlotForm.classList.add('d-none');
    }

    window.selectSlot = function(slotId, btnElement) {
        window.selectedSlotId = slotId;
        document.querySelectorAll('.time-slot-btn.active').forEach(btn => btn.classList.remove('active'));
        btnElement.classList.add('active');
        if (els.confirmBtn) els.confirmBtn.classList.remove('d-none');
    }

    window.bookSlot = function(slotId) {
        if (slotId) window.location.href = `/appointments/create/${slotId}/`;
    }

    window.deleteSlot = async function(slotId) {
        if (!slotId || !confirm("Удалить этот слот?")) return;
        try {
            const response = await fetch(`/appointments/delete_slot/${slotId}/`, {
                method: 'POST', headers: { 'X-CSRFToken': csrfToken }
            });
            if (response.ok) {
                await loadSlots(currentDate.getFullYear(), currentDate.getMonth() + 1);
                showTemporaryMessage("Слот удален.", "success");
                els.timeSlots.classList.add('d-none');
            }
        } catch (e) {
            showTemporaryMessage("Ошибка удаления.", "danger");
        }
    }

    window.openCreateSlotModal = function(dateString) {
        if (!window.isLawyer || !els.createSlotForm) return;
        els.createSlotForm.classList.remove('d-none');
        if (els.addTimeBtn) els.addTimeBtn.style.display = 'none';
        els.createSlotForm.scrollIntoView({ behavior: 'smooth' });
    }

    window.hideCreateSlotForm = function() {
        if (els.createSlotForm) els.createSlotForm.classList.add('d-none');
        if (els.addTimeBtn) els.addTimeBtn.style.display = 'block';
    }

    window.createSlot = async function() {
        if (!els.slotStartTimeSelect.value) return;
        try {
            const response = await fetch('/appointments/create_slot_from_day/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
                body: JSON.stringify({ date: window.selectedDateForSlot, startTime: els.slotStartTimeSelect.value })
            });
            if (response.ok) {
                hideCreateSlotForm();
                await loadSlots(currentDate.getFullYear(), currentDate.getMonth() + 1);
                showTemporaryMessage('Слот создан.', "success");
            } else {
                showTemporaryMessage("Ошибка создания", "danger");
            }
        } catch (e) {
            showTemporaryMessage("Ошибка сети", "danger");
        }
    }

    loadSlots(currentDate.getFullYear(), currentDate.getMonth() + 1);
});