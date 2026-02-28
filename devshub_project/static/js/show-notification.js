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
