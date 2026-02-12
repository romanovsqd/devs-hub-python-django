import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from cards import cardset_services

from . import cardsetprogress_services


@login_required
@require_POST
def cardset_toggle_study(request, cardset_id):
    cardset = cardset_services.get_user_created_or_saved_cardset_by_id(
        cardset_id, request.user
    )

    is_studying = cardsetprogress_services.toggle_cardset_study_for_user(
        cardset, request.user
    )

    if is_studying:
        message = f'Теперь вы изучаете колоду {cardset.title}'
        button_text = 'Удалить из изучаемых'
    else:
        message = f'Вы больше не изучаете колоду {cardset.title}'
        button_text = 'Добавить в изучаемые'

    return JsonResponse({
        'message': message,
        'button_text': button_text,
    })


@login_required
def review(request):
    return render(request, 'repetitions/review.html')


@login_required
def next_card(request):
    card_data = cardsetprogress_services.get_next_card_for_review(request.user)

    if card_data:
        return JsonResponse(card_data)
    else:
        return JsonResponse({'done': True})


@login_required
@require_POST
def submit(request, cardset_id, card_id):
    data = json.loads(request.body)
    quality = int(data.get('quality', 0))

    card_progress = (
        cardsetprogress_services.get_cardset_card_progress_for_user(
            cardset_id=cardset_id,
            card_id=card_id,
            user=request.user,
        )
    )

    progress = cardsetprogress_services.apply_sm2(card_progress, quality)

    return JsonResponse({
        'cardset_id': cardset_id,
        'card_id': card_id,
        'next_review_date': progress.next_review_date.isoformat(),
        'interval': progress.interval,
        'efactor': progress.efactor,
        'repetitions': progress.repetitions,
    })
