const toggleForm = document.querySelector("[data-js-toggle-save-form]");

if (toggleForm) {
  const toggleButton = toggleForm.querySelector("[data-js-toggle-button]");
  const exportButton = toggleForm.querySelector("[data-js-export-button]");

  toggleForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    try {
      const csrftoken = Cookies.get("csrftoken");

      const response = await fetch(toggleForm.action, {
        method: toggleForm.method,
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
      exportButton.classList.toggle("inactive");
      toggleButton.textContent = data.is_saved
        ? "Удалить колоду из моего профиля"
        : "Сохранить колоду в мой профиль";

      showNotification(data.message, data.is_saved);
    } catch (error) {
      console.error(error);
      showNotification("Произошла ошибка. Попробуйте снова.");
    }
  });
}
