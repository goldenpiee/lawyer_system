function showTemporaryMessage(message, type = 'info') {
    console.log(`Attempting to show message: "${message}", type: ${type}`);
    const container = document.querySelector('.messages-container');

    if (!container) {
        console.error('Messages container (.messages-container) not found in the DOM!');
        alert(`${type.toUpperCase()}: ${message}`);
        return;
    }
    container.style.display = 'flex';

    const messageId = `temp-msg-${Date.now()}`;
    // Классы и стили для message-box берем из CSS
    const alertHTML = `
        <div id="${messageId}" class="alert alert-${type} alert-dismissible fade show message-box" role="alert">
            <span class="message-text">${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    // --- ИЗМЕНЕНИЕ ЗДЕСЬ: Вставляем В НАЧАЛО контейнера ---
    container.insertAdjacentHTML('afterbegin', alertHTML);
    // -----------------------------------------------------

    console.log(`Message HTML inserted with ID: ${messageId}`);
    const newAlert = document.getElementById(messageId);

    if (newAlert) {
        const disappearTimeout = 5000; // 5 секунд
        console.log(`Setting timeout for ${disappearTimeout}ms to dismiss message ${messageId}`);

        setTimeout(() => {
            console.log(`Attempting to dismiss message ${messageId}`);
            const elementExists = document.getElementById(messageId);
            if (elementExists) {
                 try {
                    // Добавляем класс для анимации исчезновения ПЕРЕД закрытием
                    elementExists.classList.add('fade-out');
                    // Ждем завершения анимации (600мс - как в CSS transition)
                    elementExists.addEventListener('transitionend', () => {
                        // Проверяем, что элемент все еще существует (на случай быстрых кликов)
                         if(document.body.contains(elementExists)) {
                            const alertInstance = bootstrap.Alert.getOrCreateInstance(elementExists);
                            if (alertInstance) {
                                console.log(`Closing alert instance for ${messageId}`);
                                alertInstance.close();
                            } else {
                                console.warn('Could not get Bootstrap Alert instance. Removing element directly.');
                                elementExists.remove();
                            }
                        }
                    }, { once: true }); // Выполнить слушатель только один раз

                 } catch (e) {
                    console.error('Error dismissing Bootstrap alert:', e);
                    elementExists.remove();
                 }
            } else {
                console.log(`Element ${messageId} already removed before timeout.`);
            }
        }, disappearTimeout);
    } else {
         console.error('Could not find the newly added alert element by ID:', messageId);
    }
}
document.addEventListener('DOMContentLoaded', function() {
    // Например, код для скрытия Django messages
    const djangoMessageAlerts = document.querySelectorAll('.messages-container .alert:not([id^="temp-msg-"])'); // Выбираем только Django сообщения
     if (djangoMessageAlerts.length > 0) {
        setTimeout(() => {
            djangoMessageAlerts.forEach(el => {
                 el.classList.add('fade-out');
                 el.addEventListener('transitionend', () => {
                    if(document.body.contains(el)) {
                        const alertInstance = bootstrap.Alert.getOrCreateInstance(el);
                        if (alertInstance) alertInstance.close();
                        else el.remove();
                    }
                 }, { once: true });
             });
        }, 3000); // Время для Django сообщений
     }
});