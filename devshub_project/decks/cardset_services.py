from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import CardSet


def get_all_cardsets():
    """Возврващет queryset всех наборов карточек."""
    return CardSet.objects.all()


def get_cardset_by_id(cardset_id):
    """Возвращает набор карточек по id или 404."""
    return get_object_or_404(CardSet, pk=cardset_id)


def get_cardset_cards(cardset):
    """Возращает все карточки из набора карточек."""
    return cardset.cards.all()


def get_user_created_cardset_by_id(cardset_id, user):
    """
    Возвращает набор карточек по id, если он создан пользователем, иначе 404.
    """
    return get_object_or_404(
        CardSet,
        pk=cardset_id,
        author=user
    )


def get_user_created_or_saved_cardset_by_id(cardset_id, user):
    """
    Возвращает набор карточек по id, если он создан или сохранен пользователем,
    иначе 404.
    """
    return get_object_or_404(
        CardSet,
        Q(saved_by=user) | Q(author=user),
        pk=cardset_id,
    )


def get_all_user_created_or_saved_cardsets(user):
    """
    возвращает queryset всех наборов карточек,
    которые пользователь создал или сохранил.
    """
    return CardSet.objects.filter(
        Q(author=user) | Q(saved_by=user)
    ).distinct()


def filter_sort_paginate_cardsets(
    cardsets, query, sort_by, page_number, per_page=20
):
    """
    Фильтрует, сортирует, пагинирует наборы карточек. Возвращает page_obj.
    """
    if query:
        cardsets = cardsets.filter(title__icontains=query)

    if sort_by == 'newest':
        cardsets = cardsets.order_by('-created_at')
    elif sort_by == 'oldest':
        cardsets = cardsets.order_by('created_at')

    paginator = Paginator(cardsets, per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj


def is_cardset_saved_by_user(cardset, user):
    """Проверяет сохранен ли набор карточек пользователем."""
    return cardset.saved_by.filter(pk=user.pk).exists()


def toggle_cardset_save_by_user(cardset, user):
    """Переключает состояние сохранения карточки пользователем."""
    is_saved = is_cardset_saved_by_user(cardset, user)

    if is_saved:
        user.saved_cardsets.remove(cardset)
        return False
    else:
        user.saved_cardsets.add(cardset)
        return True


def generate_cards_data_for_export(cardset_cards):
    """
    Формирует данные карточки для экспорта в txt формат.
    Возвращает генератор карточек.
    """
    for card in cardset_cards.iterator(chunk_size=1000):
        yield (
            f'#author_id: {card.author_id}\n'
            f'#card_id: {card.id}\n'
            f'{card.question}\t{card.answer}\n'
            '\n'
        )


def prepare_cardset_for_export(cardset):
    """
    Подготовливает набор карточек к экспорту.
    Возвращает кортеж (filename, cards_generator).
    """
    cardset_cards = get_cardset_cards(cardset)

    filename = f'{cardset.title}.txt'
    cards_generator = generate_cards_data_for_export(cardset_cards)

    return filename, cards_generator


def get_user_cardsets_stats(user):
    """возвращает словарь со статистикой наборов карточек для пользователя."""
    cardsets = get_all_cardsets()

    cardsets_stats = cardsets.aggregate(
        total=Count(
            'id',
            filter=Q(author=user) | Q(saved_by=user),
            distinct=True
        ),
        created=Count(
            'id',
            filter=Q(author=user),
            distinct=True
        ),
        saved=Count(
            'id',
            filter=Q(saved_by=user),
            distinct=True
        ),
        in_study=Count(
            'id',
            filter=Q(progresses__learner=user),
            distinct=True
        ),
    )

    return cardsets_stats
