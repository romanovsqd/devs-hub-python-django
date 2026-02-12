from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import CardSetProgress
from decks import cardset_services


def get_user_cardset_progress(cardset, user):
    """Возвращает прогресс по набору карточек для пользователя."""
    return CardSetProgress.objects.filter(
        learner=user,
        cardset=cardset
    )


def get_cardset_card_progress_for_user(cardset_id, card_id, user):
    """
    Возвращает прогресс по карточке
    в конкретном наборе карточек для пользователя.
    """
    return get_object_or_404(
        CardSetProgress,
        learner=user,
        cardset_id=cardset_id,
        card_id=card_id,
    )


def is_user_studying_cardset(cardset, user):
    """проверяет изучает ли пользователь набор карточек"""
    cardset_progress = get_user_cardset_progress(cardset, user)
    return cardset_progress.exists()


def create_cardset_progress_for_user(cardset, user):
    """
    Инизиализиует прогресс изучения всех карточек в наборе для пользователя.
    """
    cardset_cards = cardset_services.get_cardset_cards(cardset)

    progress = [
        CardSetProgress(learner=user, card=card, cardset=cardset)
        for card in cardset_cards
    ]

    CardSetProgress.objects.bulk_create(
        progress,
        ignore_conflicts=True
    )


def toggle_cardset_study_for_user(cardset, user):
    """Переключает состояние изучения набора карточек пользователем."""
    is_studying = is_user_studying_cardset(cardset, user)

    if is_studying:
        get_user_cardset_progress(cardset, user).delete()
        return False
    else:
        create_cardset_progress_for_user(cardset, user)
        return True


def get_next_card_for_review(user):
    """Возвращает следующую карточку для повторения."""
    today = timezone.localdate()

    progress = (
        CardSetProgress.objects
        .filter(
            learner=user,
            next_review_date__date__lte=today
        )
        .select_related('card')
        .order_by('next_review_date')
        .first()
    )

    if not progress:
        return None

    card_data = {
        'card_id': progress.card_id,
        'cardset_id': progress.cardset_id,
        'question': progress.card.question,
        'answer': progress.card.answer,
    }

    return card_data


def apply_sm2(progress, quality):
    """
    Применяет алгоритм интервального повторения на основе SM-2 к карточке.
    """
    now = timezone.now()

    if quality < 3:
        progress.repetitions = 0
        progress.interval = 0
        progress.next_review_date = now
    else:
        progress.efactor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        progress.efactor = max(progress.efactor, 1.3)

        progress.repetitions += 1

        if progress.repetitions == 1:
            progress.interval = 1
        elif progress.repetitions == 2:
            progress.interval = 6
        else:
            progress.interval = round(progress.interval * progress.efactor)

        progress.next_review_date = now + timedelta(days=progress.interval)

    progress.last_review_date = now.date()
    progress.save()

    return progress


def get_user_studying_cardsets_ids(user):
    """Возращает id изучаемых пользователем наборов карточек."""
    return CardSetProgress.objects.filter(
        learner=user,
    ).values_list('cardset_id', flat=True)
