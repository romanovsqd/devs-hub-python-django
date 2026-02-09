from datetime import timedelta
import json
from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import card_services, cardset_services

from .models import CardSet, CardSetProgress
from .forms import CardForm, CardSetForm


@login_required
def card_list(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    cards = card_services.get_all_cards()

    cards = card_services.filter_sort_paginate_cards(
        cards,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'cards': cards,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'cards/cards/card_list.html', context)


@login_required
def card_detail(request, card_id):
    card = card_services.get_card_by_id(card_id)

    is_saved = card_services.is_card_saved_by_user(card, request.user)

    context = {
        'card': card,
        'is_saved': is_saved,
    }
    return render(request, 'cards/cards/card_detail.html', context)


@login_required
def card_create(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.author = request.user
            card.save()
            return redirect(card.get_absolute_url())
    else:
        form = CardForm()

    context = {
        'form': form,
    }
    return render(request, 'cards/cards/card_form.html', context)


@login_required
def card_update(request, card_id):
    card = card_services.get_user_created_card_by_id(card_id, request.user)

    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            card = form.save()
            return redirect(card.get_absolute_url())
    else:
        form = CardForm(instance=card)

    context = {
        'form': form,
    }
    return render(request, 'cards/cards/card_form.html', context)


@login_required
def card_delete(request, card_id):
    card = card_services.get_user_created_card_by_id(card_id, request.user)

    if request.method == 'POST':
        card.delete()
        return redirect('cards:card_list')

    context = {
        'card': card
    }
    return render(request, 'cards/cards/card_confirm_delete.html', context)


@login_required
@require_POST
def card_toggle_save(request, card_id):
    card = card_services.get_card_by_id(card_id)

    is_card_saved = card_services.toggle_card_save_by_user(card, request.user)

    if is_card_saved:
        message = 'Карточка сохранена в ваш профиль'
        button_text = 'Удалить из моего профиля'
    else:
        message = 'Карточка удалена из вашего профиля'
        button_text = 'Сохранить в мой профиль'

    return JsonResponse({
        'message': message,
        'button_text': button_text,
    })


@login_required
def card_export(request, card_id):
    card = card_services.get_user_created_or_saved_card_by_id(
        card_id, request.user
    )

    filename, content = card_services.prepare_card_for_export(card)

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; '
        f"filename*=UTF-8''{quote(filename)}"
    )
    response.write(content)

    return response


@login_required
def cardset_list(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    cardsets = cardset_services.get_all_cardsets()

    cardsets = cardset_services.filter_sort_paginate_cardsets(
        cardsets,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'cardsets': cardsets,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'cards/cardsets/cardset_list.html', context)


@login_required
def cardset_detail(request, cardset_id):
    cardset = cardset_services.get_cardset_by_id(cardset_id)
    cards = cardset_services.get_cardet_cards(cardset)

    is_saved = cardset_services.is_cardset_saved_by_user(cardset, request.user)

    context = {
        'cardset': cardset,
        'cards': cards,
        'is_saved': is_saved,
    }
    return render(request, 'cards/cardsets/cardset_detail.html', context)


@login_required
def cardset_create(request):
    if request.method == 'POST':
        form = CardSetForm(request.POST, user=request.user)
        if form.is_valid():
            cardset = form.save(commit=False)
            cardset.author = request.user
            cardset.save()
            form.save_m2m()
            return redirect(cardset.get_absolute_url())
    else:
        form = CardSetForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'cards/cardsets/cardset_form.html', context)


@login_required
def cardset_update(request, cardset_id):
    cardset = cardset_services.get_user_created_cardset_by_id(
        cardset_id, request.user
    )

    if request.method == 'POST':
        form = CardSetForm(request.POST, instance=cardset, user=request.user)
        if form.is_valid():
            cardset = form.save()
            return redirect(cardset.get_absolute_url())
    else:
        form = CardSetForm(instance=cardset, user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'cards/cardsets/cardset_form.html', context)


@login_required
def cardset_delete(request, cardset_id):
    cardset = cardset_services.get_user_created_cardset_by_id(
        cardset_id, request.user
    )

    if request.method == 'POST':
        cardset.delete()
        return redirect('cardsets:cardset_list')

    context = {
        'cardset': cardset
    }
    return render(request, 'cards/cardsets/cardset_confirm_delete.html', context)


@login_required
@require_POST
def cardset_toggle_save(request, cardset_id):
    cardset = cardset_services.get_cardset_by_id(cardset_id)

    is_cardset_saved = cardset_services.toggle_cardset_save_by_user(
        cardset, request.user
    )

    if is_cardset_saved:
        message = 'Набор карточек сохранен в ваш профиль'
        button_text = 'Удалить из моего профиля'
    else:
        message = 'Набор карточек удален из вашего профиля'
        button_text = 'Сохранить в мой профиль'

    return JsonResponse({
        'message': message,
        'button_text': button_text,
    })


@login_required
def cardset_export(request, cardset_id):
    cardset = cardset_services.get_user_created_or_saved_cardset_by_id(
        cardset_id, request.user
    )

    filename, cards_generator = cardset_services.prepare_cardset_for_export(
        cardset
    )

    response = StreamingHttpResponse(
        cards_generator,
        content_type='text/plain; charset=utf-8'
    )
    response['Content-Disposition'] = (
        'attachment; '
        f"filename*=UTF-8''{quote(filename)}"
    )

    return response


@login_required
@require_POST
def cardset_toggle_study(request, cardset_id):
    cardset = get_object_or_404(
        CardSet,
        pk=cardset_id,
    )

    progress_qs = CardSetProgress.objects.filter(
        learner=request.user,
        cardset=cardset
    )

    is_studying = progress_qs.exists()

    if is_studying:
        progress_qs.delete()
        message = f'Вы больше не изучаете колоду {cardset.title}'
        button_text = 'Добавить в изучаемые'
    else:
        cards = cardset.cards.all()

        CardSetProgress.objects.bulk_create([
            CardSetProgress(
                learner=request.user,
                card=card,
                cardset=cardset
            )
            for card in cards
        ],
            ignore_conflicts=True
        )
        message = f'Теперь вы изучаете колоду {cardset.title}'
        button_text = 'Удалить из изучаемых'

    return JsonResponse({
        'message': message,
        'button_text': button_text,
    })


@login_required
def review(request):
    return render(request, 'cards/study/review.html')


@login_required
def next_card(request):
    today = timezone.localdate()

    progress = (
        CardSetProgress.objects
        .filter(
            learner=request.user,
            next_review_date__date=today
        )
        .select_related('card')
        .order_by('next_review_date')
        .first()
    )

    if not progress:
        return JsonResponse({
            'done': True
        })

    card = progress.card
    cardset = progress.cardset

    return JsonResponse({
        'card_id': card.id,
        'question': card.question,
        'answer': card.answer,
        'cardset_id': cardset.id,
    })


@login_required
@require_POST
def submit(request, cardset_id, card_id):
    data = json.loads(request.body)
    quality = int(data.get('quality'))

    progress = get_object_or_404(
        CardSetProgress,
        learner=request.user,
        cardset_id=cardset_id,
        card_id=card_id,
    )

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

    return JsonResponse({
        'cardset_id': cardset_id,
        'card_id': card_id,
        'next_review_date': progress.next_review_date.isoformat(),
        'interval': progress.interval,
        'efactor': progress.efactor,
        'repetitions': progress.repetitions,
    })
