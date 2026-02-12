const toggleSaveForms = document.querySelectorAll('[data-js-toggle-save-form]');

if (toggleSaveForms) {
  toggleSaveForms.forEach((form) => {
    const toggleButton = form.querySelector('[data-js-toggle-button]');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      try {
        const csrftoken = Cookies.get('csrftoken');

        const response = await fetch(form.action, {
          method: form.method,
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
  });
}

function showNotification(message) {
  const notification = document.createElement('div');
  notification.textContent = message;

  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}
