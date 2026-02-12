from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CardSetForm
from . import cardset_services


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
    cards = cardset_services.get_cardset_cards(cardset)

    is_saved = cardset_services.is_cardset_saved_by_user(cardset, request.user)

    context = {
        'cardset': cardset,
        'cards': cards,
        'is_saved': is_saved,
    }
    return render(request, 'cards/cardsets/cardset_detail.html', context)


@login_required
def cardset_create(request):
    form = CardSetForm(request.POST or None, user=request.user)

    if form.is_valid():
        cardset = form.save(commit=False)
        cardset.author = request.user
        cardset.save()
        form.save_m2m()
        return redirect(cardset.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, 'cards/cardsets/cardset_form.html', context)


@login_required
def cardset_update(request, cardset_id):
    cardset = cardset_services.get_user_created_cardset_by_id(
        cardset_id, request.user
    )

    form = CardSetForm(
        request.POST or None, instance=cardset, user=request.user
    )

    if form.is_valid():
        cardset = form.save()
        return redirect(cardset.get_absolute_url())

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
        return redirect('cardset_list')

    context = {
        'cardset': cardset
    }
    return render(
        request, 'cards/cardsets/cardset_confirm_delete.html', context
    )


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
