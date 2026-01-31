from datetime import timedelta
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Card, CardSet, CardSetProgress
from .forms import CardForm, CardSetForm


@login_required
def card_list(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by')

    cards = Card.objects.all()

    if query:
        cards = cards.filter(question__icontains=query)

    if sort_by == 'newest':
        cards = cards.order_by('-created_at')
    elif sort_by == 'oldest':
        cards = cards.order_by('created_at')

    context = {
        'cards': cards
    }
    return render(request, 'cards/cards/card_list.html', context)


@login_required
def card_detail(request, card_id):
    card = get_object_or_404(Card, pk=card_id)

    is_saved = request.user.saved_cards.filter(pk=card.pk).exists()

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
    card = get_object_or_404(
        Card,
        pk=card_id,
        author=request.user
    )

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
    card = get_object_or_404(
        Card,
        pk=card_id,
        author=request.user
    )

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
    card = get_object_or_404(
        Card,
        pk=card_id,
    )

    is_saved = request.user.saved_cards.filter(pk=card.pk).exists()

    if is_saved:
        request.user.saved_cards.remove(card)
        message = 'Карточка удалена из вашего профиля'
        button_text = 'Сохранить в мой профиль'
    else:
        request.user.saved_cards.add(card)
        message = 'Карточка сохранена в ваш профиль'
        button_text = 'Удалить из моего профиля'

    return JsonResponse({
        'message': message,
        'button_text': button_text,
    })


@login_required
def cardset_list(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')

    cardsets = CardSet.objects.all()

    if query:
        cardsets = cardsets.filter(title__icontains=query)

    if sort_by == 'newest':
        cardsets = cardsets.order_by('-created_at')
    elif sort_by == 'oldest':
        cardsets = cardsets.order_by('created_at')

    context = {
        'cardsets': cardsets
    }
    return render(request, 'cards/cardsets/cardset_list.html', context)


@login_required
def cardset_detail(request, cardset_id):
    cardset = get_object_or_404(CardSet, pk=cardset_id)
    cards = cardset.cards.all()

    is_saved = request.user.saved_cardsets.filter(pk=cardset.pk).exists()

    context = {
        'cardset': cardset,
        'cards': cards,
        'is_saved': is_saved,
    }
    return render(request, 'cards/cardsets/cardset_detail.html', context)


@login_required
def cardset_create(request):
    cards_queryset = Card.objects.filter(
        Q(author=request.user) | Q(saved_by=request.user)
    ).distinct()

    if request.method == 'POST':
        form = CardSetForm(request.POST, cards_queryset=cards_queryset)
        if form.is_valid():
            cardset = form.save(commit=False)
            cardset.author = request.user
            cardset.save()
            form.save_m2m()
            return redirect(cardset.get_absolute_url())
    else:
        form = CardSetForm(cards_queryset=cards_queryset)

    context = {
        'form': form,
    }
    return render(request, 'cards/cardsets/cardset_form.html', context)


@login_required
def cardset_update(request, cardset_id):
    cardset = get_object_or_404(
        CardSet,
        pk=cardset_id,
        author=request.user
    )

    if request.method == 'POST':
        form = CardSetForm(request.POST, instance=cardset)
        if form.is_valid():
            cardset = form.save()
            return redirect(cardset.get_absolute_url())
    else:
        form = CardSetForm(instance=cardset)

    context = {
        'form': form,
    }
    return render(request, 'cards/cardsets/cardset_form.html', context)


@login_required
def cardset_delete(request, cardset_id):
    cardset = get_object_or_404(
        CardSet,
        pk=cardset_id,
        author=request.user
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
    cardset = get_object_or_404(
        CardSet,
        pk=cardset_id,
    )

    is_saved = request.user.saved_cardsets.filter(pk=cardset.pk).exists()

    if is_saved:
        request.user.saved_cardsets.remove(cardset)
        message = 'Набор карточек удален из вашего профиля'
        button_text = 'Сохранить в мой профиль'
    else:
        request.user.saved_cardsets.add(cardset)
        message = 'Набор карточек сохранен в ваш профиль'
        button_text = 'Удалить из моего профиля'

    return JsonResponse({
        'message': message,
        'button_text': button_text,
    })


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
