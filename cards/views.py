from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
def card_create(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
    else:
        form = CardForm()

    context = {
        'form': form,
    }
    return render(request, 'cards/card_form.html', context)
