from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import Deck


def get_all_decks():
    """Возврващет queryset всех наборов карточек."""
    return Deck.objects.all().select_related("author").prefetch_related("saved_by")


def get_deck_by_id(deck_id):
    """Возвращает набор карточек по id или 404."""
    return get_object_or_404(Deck, pk=deck_id)


def get_deck_cards(deck):
    """Возращает все карточки из набора карточек."""
    return deck.cards.all().select_related("author").prefetch_related("saved_by")


def get_user_created_deck_by_id(deck_id, user):
    """
    Возвращает набор карточек по id, если он создан пользователем, иначе 404.
    """
    return get_object_or_404(Deck, pk=deck_id, author=user)


def get_user_created_or_saved_deck_by_id(deck_id, user):
    """
    Возвращает набор карточек по id, если он создан или сохранен пользователем,
    иначе 404.
    """
    return get_object_or_404(
        Deck,
        Q(saved_by=user) | Q(author=user),
        pk=deck_id,
    )


def get_all_user_created_or_saved_decks(user):
    """
    возвращает queryset всех наборов карточек,
    которые пользователь создал или сохранил.
    """
    return (
        Deck.objects.filter(
            Q(author=user) | Q(saved_by=user),
        )
        .select_related("author")
        .prefetch_related("saved_by")
        .distinct()
    )


def filter_sort_paginate_decks(decks, query, sort_by, page_number, per_page=20):
    """
    Фильтрует, сортирует, пагинирует наборы карточек. Возвращает page_obj.
    """
    if query:
        decks = decks.filter(title__icontains=query)

    if sort_by == "newest":
        decks = decks.order_by("-created_at")
    elif sort_by == "oldest":
        decks = decks.order_by("created_at")

    paginator = Paginator(decks, per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj


def is_deck_saved_by_user(deck, user):
    """Проверяет сохранен ли набор карточек пользователем."""
    return user in deck.saved_by.all()


def toggle_deck_save_by_user(deck, user):
    """Переключает состояние сохранения карточки пользователем."""
    is_saved = is_deck_saved_by_user(deck, user)

    if is_saved:
        user.saved_decks.remove(deck)
        return False
    else:
        user.saved_decks.add(deck)
        return True


def generate_cards_data_for_export(deck_cards):
    """
    Формирует данные карточки для экспорта в txt формат.
    Возвращает генератор карточек.
    """
    for card in deck_cards.iterator(chunk_size=1000):
        yield (
            f"#author_id: {card.author_id}\n"
            f"#card_id: {card.id}\n"
            f"{card.question}\t{card.answer}\n"
            "\n"
        )


def prepare_deck_for_export(deck):
    """
    Подготовливает набор карточек к экспорту.
    Возвращает кортеж (filename, cards_generator).
    """
    deck_cards = get_deck_cards(deck)

    filename = f"{deck.title}.txt"
    cards_generator = generate_cards_data_for_export(deck_cards)

    return filename, cards_generator


def get_user_decks_stats(user):
    """возвращает словарь со статистикой наборов карточек для пользователя."""
    decks = get_all_decks()

    decks_stats = decks.aggregate(
        total=Count(
            "id",
            filter=Q(author=user) | Q(saved_by=user),
            distinct=True,
        ),
        created=Count(
            "id",
            filter=Q(author=user),
            distinct=True,
        ),
        saved=Count(
            "id",
            filter=Q(saved_by=user),
            distinct=True,
        ),
        in_study=Count(
            "id",
            filter=Q(progresses__learner=user),
            distinct=True,
        ),
    )
    decks_stats = decks.aggregate()

    return decks_stats
