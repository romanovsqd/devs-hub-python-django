from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Card, CardSet
from .forms import CardForm, CardSetForm


@login_required
def card_list(request):
    query = request.GET.get('query', '')

    if query:
        cards = Card.objects.filter(question__icontains=query)
    else:
        cards = Card.objects.all()

    context = {
        'cards': cards
    }
    return render(request, 'cards/card_list.html', context)


@login_required
def card_detail(request, card_id):
    card = get_object_or_404(Card, pk=card_id)

    context = {
        'card': card
    }
    return render(request, 'cards/card_detail.html', context)


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
    return render(request, 'cards/card_form.html', context)


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
    return render(request, 'cards/card_form.html', context)


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
    return render(request, 'cards/card_confirm_delete.html', context)


@login_required
def cardset_list(request):
    query = request.GET.get('query', '')

    if query:
        cardsets = CardSet.objects.filter(title__icontains=query)
    else:
        cardsets = CardSet.objects.all()

    context = {
        'cardsets': cardsets
    }
    return render(request, 'cardsets/cardset_list.html', context)


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
    return render(request, 'cardsets/cardset_detail.html', context)


@login_required
def cardset_create(request):
    if request.method == 'POST':
        form = CardSetForm(request.POST)
        if form.is_valid():
            cardset = form.save(commit=False)
            cardset.author = request.user
            cardset.save()
            form.save_m2m()
            return redirect(cardset.get_absolute_url())
    else:
        form = CardSetForm()

    context = {
        'form': form,
    }
    return render(request, 'cardsets/cardset_form.html', context)


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
    return render(request, 'cardsets/cardset_form.html', context)


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
    return render(request, 'cardsets/cardset_confirm_delete.html', context)


@login_required
@require_POST
def cardset_save(request, cardset_id):
    cardset = get_object_or_404(
        CardSet,
        pk=cardset_id,
    )

    is_saved = request.user.saved_cardsets.filter(pk=cardset.pk).exists()

    if not is_saved:
        request.user.saved_cardsets.add(cardset)

    return JsonResponse({
        'message': 'Набор карточек сохранен в ваш профиль'
    })


@login_required
@require_POST
def cardset_remove(request, cardset_id):
    cardset = get_object_or_404(
        CardSet,
        pk=cardset_id,
    )

    is_saved = request.user.saved_cardsets.filter(pk=cardset.pk).exists()

    if is_saved:
        request.user.saved_cardsets.remove(cardset)

    return JsonResponse({
        'message': 'Набор карточек удален из вашего профиля'
    })


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
