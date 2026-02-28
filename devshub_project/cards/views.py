from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import services
from .forms import CardForm


def card_list(request):
    user = request.user if request.user.is_authenticated else None

    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    cards = services.filter_sort_paginate_cards(
        cards=services.get_cards_with_saved_status(user=user),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
    )

    context = {
        "cards": cards,
        "query": query,
        "sort_by": sort_by,
    }
    return render(request, "cards/card_list.html", context)


def card_detail(request, card_id):
    user = request.user if request.user.is_authenticated else None

    card = services.get_card_with_saved_status(card_id=card_id, user=user)

    context = {"card": card}
    return render(request, "cards/card_detail.html", context)


@login_required
def card_create(request):
    if request.method == "POST":
        form = CardForm(request.POST)

        if form.is_valid():
            card = services.create_card(
                **form.cleaned_data,
                author=request.user,
            )
            return redirect(card.get_absolute_url())
    else:
        form = CardForm()

    context = {"form": form}
    return render(request, "cards/card_form.html", context)


@login_required
def card_update(request, card_id):
    card = services.get_card_created_by_user(card_id=card_id, user=request.user)

    if request.method == "POST":
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            services.update_card(
                **form.cleaned_data,
                card=card,
            )
            return redirect(card.get_absolute_url())
    else:
        form = CardForm(instance=card)

    context = {
        "form": form,
    }

    return render(request, "cards/card_form.html", context)


@login_required
def card_delete(request, card_id):
    card = services.get_card_created_by_user(card_id=card_id, user=request.user)

    if request.method == "POST":
        services.delete_card(card=card)
        return redirect("card_list")

    context = {
        "card": card,
    }

    return render(request, "cards/card_confirm_delete.html", context)


@login_required
@require_POST
def card_toggle_save(request, card_id):
    card = services.get_card_with_saved_status(card_id=card_id, user=request.user)

    success, result = services.toggle_card_save_by_user(card=card, user=request.user)

    return JsonResponse({"success": success, "message": result})


@login_required
def card_export(request, card_id):
    card = services.get_card_created_or_saved_by_user(
        card_id=card_id, user=request.user
    )

    filename, content = services.generate_card_data_for_export(card=card)

    response = HttpResponse(content_type="text/plain")
    response["Content-Disposition"] = (
        "attachment; " f"filename*=UTF-8''{quote(filename)}"
    )
    response.write(content)

    return response
