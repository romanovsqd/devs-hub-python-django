const ctx = document.querySelector("[data-js-stats-canvas]");

const totalCompletedKatas = ctx.dataset.jsTotalCompletedKatas;
const cardsInStudy = ctx.dataset.jsCardsInStudy;
const decksInStudy = ctx.dataset.jsDecksInStudy;
const totalProjects = ctx.dataset.jsTotalProjects;

new Chart(ctx, {
  type: "doughnut",
  data: {
    labels: [
      "Решенные задачи codewars",
      "Карточки в изучении",
      "Колоды в изучении",
      "Проекты",
    ],
    datasets: [
      {
        data: [totalCompletedKatas, cardsInStudy, decksInStudy, totalProjects],
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
