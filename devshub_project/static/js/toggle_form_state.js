const toggleSaveForms = document.querySelectorAll("[data-js-toggle-save-form]");

if (toggleSaveForms) {
  toggleSaveForms.forEach((form) => {
    const toggleButton = form.querySelector("[data-js-toggle-button]");
    const exportButton = form.querySelector("[data-js-export-button]");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      try {
        const csrftoken = Cookies.get("csrftoken");

        const response = await fetch(form.action, {
          method: form.method,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
          },
        });

        if (!response.ok) {
          throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const data = await response.json();

        const isPrimary = toggleButton.classList.contains("primary");

        toggleButton.classList.toggle("danger", isPrimary);
        toggleButton.classList.toggle("primary", !isPrimary);

        if (exportButton) {
          exportButton.classList.toggle("inactive");
        }
        toggleButton.textContent = data.button_text;

        showNotification(data.message, data.success);
      } catch (error) {
        console.error(error);
        showNotification("Произошла ошибка. Попробуйте снова.");
      }
    });
  });
}

function showNotification(message, success = false) {
  const container = document.getElementById("notifications");

  const notification = document.createElement("div");
  notification.className = `
    w-full rounded-md py-2 px-4 text-md font-medium border transition-all duration-300
    ${success ? "success" : "danger"}
    opacity-0 translate-x-4
  `;

  notification.textContent = message;
  container.appendChild(notification);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      notification.classList.remove("opacity-0", "translate-x-4");
    });
  });

  setTimeout(() => {
    notification.classList.add("opacity-0", "translate-x-4");
    setTimeout(() => notification.remove(), 3000);
  }, 3000);
}
