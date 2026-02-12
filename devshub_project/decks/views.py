from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import services
from .forms import DeckForm


@login_required
def deck_list(request):
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    decks = services.filter_sort_paginate_decks(
        decks=services.get_all_decks(),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    context = {
        "decks": decks,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "decks/deck_list.html", context)


@login_required
def deck_detail(request, deck_id):
    deck = services.get_deck_by_id(deck_id=deck_id)
    is_saved = services.is_deck_saved_by_user(deck=deck, user=request.user)

    cards = services.get_deck_cards(deck=deck)

    context = {
        "deck": deck,
        "cards": cards,
        "is_saved": is_saved,
    }

    return render(request, "decks/deck_detail.html", context)


@login_required
def deck_create(request):
    form = DeckForm(request.POST or None, user=request.user)

    if form.is_valid():
        deck = form.save(commit=False)
        deck.author = request.user
        deck.save()
        form.save_m2m()
        return redirect(deck.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, "decks/deck_form.html", context)


@login_required
def deck_update(request, deck_id):
    deck = services.get_user_created_deck_by_id(deck_id=deck_id, user=request.user)

    form = DeckForm(request.POST or None, instance=deck, user=request.user)

    if form.is_valid():
        deck = form.save()
        return redirect(deck.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, "decks/deck_form.html", context)


@login_required
def deck_delete(request, deck_id):
    deck = services.get_user_created_deck_by_id(deck_id=deck_id, user=request.user)

    if request.method == "POST":
        deck.delete()
        return redirect("deck_list")

    context = {
        "deck": deck,
    }

    return render(request, "decks/deck_confirm_delete.html", context)


@login_required
@require_POST
def deck_toggle_save(request, deck_id):
    deck = services.get_deck_by_id(deck_id=deck_id)
    is_deck_saved = services.toggle_deck_save_by_user(deck=deck, user=request.user)

    if is_deck_saved:
        message = "Набор карточек сохранен в ваш профиль"
        button_text = "Удалить из моего профиля"
    else:
        message = "Набор карточек удален из вашего профиля"
        button_text = "Сохранить в мой профиль"

    return JsonResponse(
        {
            "message": message,
            "button_text": button_text,
        }
    )


@login_required
def deck_export(request, deck_id):
    deck = services.get_user_created_or_saved_deck_by_id(
        deck_id=deck_id, user=request.user
    )
    filename, cards_generator = services.prepare_deck_for_export(deck=deck)

    response = StreamingHttpResponse(
        cards_generator, content_type="text/plain; charset=utf-8"
    )
    response["Content-Disposition"] = (
        "attachment; " f"filename*=UTF-8''{quote(filename)}"
    )

    return response
