from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import services
from .forms import CardForm


@login_required
def card_list(request):
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    cards = services.filter_sort_paginate_cards(
        cards=services.get_all_cards(),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    context = {
        "cards": cards,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "cards/card_list.html", context)


@login_required
def card_detail(request, card_id):
    card = services.get_card_by_id(card_id=card_id)
    is_saved = services.is_card_saved_by_user(card=card, user=request.user)

    context = {
        "card": card,
        "is_saved": is_saved,
    }

    return render(request, "cards/card_detail.html", context)


@login_required
def card_create(request):
    form = CardForm(request.POST or None)

    if form.is_valid():
        card = services.create_card(
            question=form.cleaned_data["question"],
            answer=form.cleaned_data["answer"],
            author=request.user,
        )
        return redirect(card.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, "cards/card_form.html", context)


@login_required
def card_update(request, card_id):
    card = services.get_user_created_card_by_id(card_id=card_id, user=request.user)

    form = CardForm(request.POST or None, instance=card)

    if form.is_valid():
        services.update_card(
            card=card,
            question=form.cleaned_data["question"],
            answer=form.cleaned_data["answer"],
        )
        return redirect(card.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, "cards/card_form.html", context)


@login_required
def card_delete(request, card_id):
    card = services.get_user_created_card_by_id(card_id=card_id, user=request.user)

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
    card = services.get_card_by_id(card_id=card_id)
    is_card_saved = services.toggle_card_save_by_user(card=card, user=request.user)

    if is_card_saved:
        message = "Карточка сохранена в ваш профиль"
        button_text = "Удалить карточку из моего профиля"
    else:
        message = "Карточка удалена из вашего профиля"
        button_text = "Сохранить карточку в мой профиль"

    return JsonResponse(
        {
            "success": is_card_saved,
            "message": message,
            "button_text": button_text,
        }
    )


@login_required
def card_export(request, card_id):
    card = services.get_user_created_or_saved_card_by_id(
        card_id=card_id, user=request.user
    )
    filename, content = services.generate_card_data_for_export(card=card)

    response = HttpResponse(content_type="text/plain")
    response["Content-Disposition"] = (
        "attachment; " f"filename*=UTF-8''{quote(filename)}"
    )
    response.write(content)

    return response
