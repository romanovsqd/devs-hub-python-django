import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from decks import services as deck_services

from . import services


@login_required
@require_POST
def deck_toggle_study(request, deck_id):
    deck = deck_services.get_user_created_or_saved_deck_by_id(
        deck_id=deck_id, user=request.user
    )

    is_studying = services.toggle_deck_study_for_user(deck=deck, user=request.user)

    if is_studying:
        message = f"Вы изучаете {deck.title}"
        button_text = "Удалить из изучаемых"
    else:
        message = f"Вы не изучаете {deck.title}"
        button_text = "Добавить в изучаемые"

    return JsonResponse(
        {
            "success": is_studying,
            "message": message,
            "button_text": button_text,
        }
    )


@login_required
def review(request):
    return render(request, "repetitions/review.html")


@login_required
def next_card(request):
    card_data = services.get_next_card_for_review(user=request.user)

    if card_data:
        return JsonResponse(card_data)
    else:
        return JsonResponse({"done": True})


@login_required
@require_POST
def submit(request, deck_id, card_id):
    data = json.loads(request.body)
    quality = int(data.get("quality", 0))

    card_progress = services.get_deck_card_progress_for_user(
        deck_id=deck_id,
        card_id=card_id,
        user=request.user,
    )

    progress = services.apply_sm2(progress=card_progress, quality=quality)

    return JsonResponse(
        {
            "deck_id": deck_id,
            "card_id": card_id,
            "next_review_date": progress.next_review_date.isoformat(),
            "interval": progress.interval,
            "efactor": progress.efactor,
            "repetitions": progress.repetitions,
        }
    )
