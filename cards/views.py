from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Card
from .forms import CardForm


@login_required
def card_list(request):
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
            card.user = request.user
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
        user=request.user
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
        user=request.user
    )

    if request.method == 'POST':
        card.delete()
        return redirect('cards:card_list')

    context = {
        'card': card
    }
    return render(request, 'cards/card_confirm_delete.html', context)
