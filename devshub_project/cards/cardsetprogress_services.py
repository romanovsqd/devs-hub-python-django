from django.utils import timezone
from . import cardset_services
from .models import CardSetProgress


def get_user_cardset_progress(cardset, user):
    return CardSetProgress.objects.filter(
        learner=user,
        cardset=cardset
    )


def is_user_studying_cardset(cardset, user):
    cardset_progress = get_user_cardset_progress(cardset, user)
    return cardset_progress.exists()


def create_cardset_progress_for_user(cardset, user):
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
    is_studying = is_user_studying_cardset(cardset, user)

    if is_studying:
        get_user_cardset_progress(cardset, user).delete()
        return False
    else:
        create_cardset_progress_for_user(cardset, user)
        return True


def get_next_card_for_review(user):
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
