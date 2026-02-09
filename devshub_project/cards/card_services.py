from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Card


def get_all_cards():
    """Возврващет queryset всех карточек."""
    return Card.objects.all()


def get_card_by_id(card_id):
    """Возвращает карточку по id или 404."""
    return get_object_or_404(Card, pk=card_id)


def get_user_created_card_by_id(card_id, user):
    """Возвращает карточку по id, если она создана пользователем, иначе 404."""
    return get_object_or_404(
        Card,
        pk=card_id,
        author=user
    )


def get_user_created_or_saved_card_by_id(card_id, user):
    """
    Возвращает карточку по id, если она создана или сохранена пользователем,
    иначе 404.
    """
    return get_object_or_404(
        Card,
        Q(saved_by=user) | Q(author=user),
        pk=card_id,
    )


def get_all_user_created_or_saved_cards(user):
    return Card.objects.filter(
        Q(author=user) | Q(saved_by=user)
    ).distinct()


def filter_sort_paginate_cards(
    cards, query, sort_by, page_number, per_page=20
):
    """Фильтрует, сортирует, пагинирует карточки. Возвращает page_obj."""
    if query:
        cards = cards.filter(question__icontains=query)

    if sort_by == 'newest':
        cards = cards.order_by('-created_at')
    elif sort_by == 'oldest':
        cards = cards.order_by('created_at')

    paginator = Paginator(cards, per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj


def is_card_saved_by_user(card, user):
    """Проверяет сохранена ли карточка пользователем."""
    return card.saved_by.filter(pk=user.pk).exists()


def toggle_card_save_by_user(card, user):
    """Переключает состояние сохранения карточки пользователем."""
    is_saved = is_card_saved_by_user(card, user)

    if is_saved:
        user.saved_cards.remove(card)
        return False
    else:
        user.saved_cards.add(card)
        return True


def generate_card_data_for_export(card):
    """
    Формирует данные карточки для экспорта в txt формат.
    Возвращает кортеж (filename, content)
    """
    filename = f'{card.question}.txt'

    content = (
        f'#author_id: {card.author.id}\n'
        f'#card_id: {card.id}\n'
        f'{card.question}\t'
        f'{card.answer}\n'
    )
    return filename, content
