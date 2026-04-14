function showTemporaryMessage(message, type = 'info') {
    const container = document.querySelector('.messages-container');
    if (!container) return;

    container.style.display = 'flex';
    const messageId = `msg-${Date.now()}`;
    const alertHTML = `
        <div id="${messageId}" class="alert alert-${type} alert-dismissible fade show message-box" role="alert">
            <span class="message-text">${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    container.insertAdjacentHTML('afterbegin', alertHTML);

    setTimeout(() => {
        const element = document.getElementById(messageId);
        if (element) {
            element.classList.add('fade-out');
            element.addEventListener('transitionend', () => {
                if (document.body.contains(element)) {
                    element.remove();
                }
            }, { once: true });
        }
    }, 5000);
}

document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.messages-container .alert:not([id^="msg-"])');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(el => {
                el.classList.add('fade-out');
                el.addEventListener('transitionend', () => el.remove(), { once: true });
            });
        }, 4000);
    }

    const fileInputs = document.querySelectorAll('.custom-file-upload input[type="file"]');
    fileInputs.forEach(function(input) {
        const display = input.closest('.custom-file-upload')?.querySelector('.file-name, .file-name-display');
        if (display) {
            input.addEventListener('change', function() {
                if (input.files.length > 0) {
                    display.textContent = input.files[0].name;
                    display.classList.remove('text-muted'); 
                } else {
                    display.textContent = 'Файл не выбран';
                    display.classList.add('text-muted');
                }
            });
        }
    });
});