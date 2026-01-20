const toggleSaveForm = document.querySelector('[data-js-toggle-save-form]');

if (toggleSaveForm) {
  const toggleButton = toggleSaveForm.querySelector('[data-js-toggle-button]');

  toggleSaveForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    try {
      const csrftoken = Cookies.get('csrftoken');

      const response = await fetch(toggleSaveForm.action, {
        method: toggleSaveForm.method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const data = await response.json();

      toggleButton.textContent = data.button_text;
      showNotification(data.message);
    } catch (error) {
      console.error(error);
      showNotification('Произошла ошибка. Попробуйте снова.');
    }
  });
}

function showNotification(message) {
  const notification = document.createElement('div');
  notification.textContent = message;

  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}
