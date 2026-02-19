const ctx = document.querySelector("[data-js-stats-canvas]");

const data = [
  Number(ctx.dataset.jsTotalCompletedKatas) || 0,
  Number(ctx.dataset.jsCardsInStudy) || 0,
  Number(ctx.dataset.jsDecksInStudy) || 0,
  Number(ctx.dataset.jsTotalProjects) || 0,
];

const hasData = data.some((value) => value > 0);

if (!hasData) {
  const message = document.createElement("p");
  message.textContent = "Пока нет данных для отображения статистики";
  message.className = "text-center text-gray-500 py-8";
  ctx.replaceWith(message);
} else {
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: [
        "Решенные задачи Codewars",
        "Карточки в изучении",
        "Колоды в изучении",
        "Проекты",
      ],
      datasets: [
        {
          data,
          backgroundColor: ["#ff85a0", "#66bdf0", "#66d666", "#ffb84d"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
}
