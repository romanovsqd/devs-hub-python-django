const toggleStudyForms = document.querySelectorAll(
  "[data-js-toggle-save-form]",
);

if (toggleStudyForms) {
  toggleStudyForms.forEach((form) => {
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

        toggleButton.textContent = data.success
          ? "Удалить из изучаемых"
          : "Добавить в изучаемые";

        if (exportButton) {
          exportButton.classList.toggle("inactive");
        }

        showNotification(data.message, data.success);
      } catch (error) {
        console.error(error);
        showNotification("Произошла ошибка. Попробуйте снова.");
      }
    });
  });
}
