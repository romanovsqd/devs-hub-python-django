const reviewContainer = document.querySelector('[data-js-review-container]');

if (reviewContainer) {
  const nextCardUrl = reviewContainer.dataset.nextCardUrl;
  const submitUrlTemplate = reviewContainer.dataset.submitUrl;

  const front = document.querySelector('[data-js-card-front]');
  const back = document.querySelector('[data-js-card-back]');
  const empty = document.querySelector('[data-js-card-empty]');

  const questionElement = front.querySelector('[data-js-card-question]');
  const answerElement = back.querySelector('[data-js-card-answer]');

  const flipButton = document.querySelector('[data-js-flip-card-button]');
  const qualityButtons = document.querySelector('[data-js-quality-buttons]');

  let currentCardId = null;
  let currentCardsetId = null;

  back.style.display = 'none';

  flipButton.addEventListener('click', () => {
    flipButton.style.display = 'none';
    back.style.display = 'block';
  });

  qualityButtons.addEventListener('click', async (e) => {
    const button = e.target.closest('button');
    if (!button || !currentCardId || !currentCardsetId) {
      return;
    }

    const submitUrl = submitUrlTemplate.replace(
      /0\/0/,
      `${currentCardsetId}/${currentCardId}`,
    );
    const csrftoken = Cookies.get('csrftoken');
    const quality = button.dataset.quality;

    try {
      const response = await fetch(submitUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ quality }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      await loadNextCard();
    } catch (error) {
      console.error('Ошибка отправки ответа', error);
    }
  });

  async function loadNextCard() {
    try {
      const response = await fetch(nextCardUrl);

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const data = await response.json();

      if (data.done) {
        front.style.display = 'none';
        back.style.display = 'none';
        empty.style.display = 'block';
        return;
      }

      currentCardId = data.card_id;
      currentCardsetId = data.cardset_id;
      questionElement.textContent = data.question;
      answerElement.textContent = data.answer;

      flipButton.style.display = 'block';
      front.style.display = 'block';
      back.style.display = 'none';
    } catch (error) {
      console.error(error);
    }
  }

  loadNextCard();
}
