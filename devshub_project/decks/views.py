from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from cards import services as card_services

from . import services
from .forms import DeckForm


def deck_list(request):
    user = request.user if request.user.is_authenticated else None

    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    decks = services.filter_sort_paginate_decks(
        decks=services.get_decks_with_saved_status(user=user),
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


def deck_detail(request, pk):
    user = request.user if request.user.is_authenticated else None

    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    deck = services.get_deck_with_saved_status(deck_id=pk, user=user)

    cards = card_services.filter_sort_paginate_cards(
        cards=services.get_deck_cards_with_saved_status(deck=deck, user=user),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    context = {
        "deck": deck,
        "cards": cards,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "decks/deck_detail.html", context)


@login_required
def deck_create(request):
    if request.method == "POST":
        form = DeckForm(request.POST, user=request.user)

        if form.is_valid():
            deck = services.create_deck(
                **form.cleaned_data,
                author=request.user,
            )
            return redirect(deck.get_absolute_url())
    else:
        form = DeckForm(user=request.user)

    context = {
        "form": form,
    }

    return render(request, "decks/deck_form.html", context)


@login_required
def deck_update(request, pk):
    deck = services.get_deck_created_by_user(deck_id=pk, user=request.user)

    if request.method == "POST":
        form = DeckForm(request.POST, instance=deck, user=request.user)

        if form.is_valid():
            services.update_deck(
                **form.cleaned_data,
                deck=deck,
            )
            return redirect(deck.get_absolute_url())
    else:
        form = DeckForm(instance=deck, user=request.user)

    context = {
        "form": form,
    }

    return render(request, "decks/deck_form.html", context)


@login_required
def deck_delete(request, pk):
    deck = services.get_deck_created_by_user(deck_id=pk, user=request.user)

    if request.method == "POST":
        services.delete_deck(deck=deck)
        return redirect("deck_list")

    context = {
        "deck": deck,
    }

    return render(request, "decks/deck_confirm_delete.html", context)


@login_required
@require_POST
def deck_toggle_save(request, pk):
    deck = services.get_deck_with_saved_status(deck_id=pk, user=request.user)

    success, message = services.toggle_deck_save_by_user(deck=deck, user=request.user)

    return JsonResponse({"success": success, "message": message})


@login_required
def deck_export(request, pk):
    deck = services.get_deck_created_or_saved_by_user(deck_id=pk, user=request.user)
    filename, cards_generator = services.prepare_deck_for_export(deck=deck)

    response = StreamingHttpResponse(
        cards_generator, content_type="text/plain; charset=utf-8"
    )
    response["Content-Disposition"] = (
        "attachment; " f"filename*=UTF-8''{quote(filename)}"
    )

    return response
