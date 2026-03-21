from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404

from repetitions import services as repetition_services

from .models import Deck


def get_decks():
    """
    Возвращает queryset всех колод.
    """
    return (
        Deck.objects.all()
        .select_related("author")
        .only("id", "title", "created_at", "updated_at", "author__username")
    )


def get_decks_with_saved_status(user=None):
    """
    Возвращает queryset колод с флагом,
    который указывает сохранена ли колода пользователем.
    """
    decks = get_decks()

    if user is not None:
        return decks.annotate(
            is_saved=Exists(user.saved_decks.filter(pk=OuterRef("pk")))
        )

    return decks


def get_deck_with_saved_status(deck_id, user=None):
    """
    Возвращает колоду с флагом,
    который указывает сохранена ли колода пользователем.
    """
    deck = get_object_or_404(get_decks_with_saved_status(user=user), pk=deck_id)

    return deck


def get_deck_created_by_user(deck_id, user):
    """
    Возвращает колоду если она создана пользователем.
    Если пользователь не является автором, или
    если колоды не существует, вернет 404.
    """
    deck = get_object_or_404(Deck.objects.filter(author=user), pk=deck_id)
    return deck


def get_decks_created_or_saved_by_user(user):
    """
    Возвращает queryset колод,
    которые созданы или сохранены пользователем.
    """
    decks = get_decks().filter(Q(author=user) | Q(saved_by=user)).distinct()
    return decks


def get_user_decks_with_saved_status(user, current_user):
    """
    Возвращает колоды созданные или сохраненные пользователем с флагом,
    который указывает сохранена ли карточка текущим пользователем.
    """
    user_decks = get_decks_created_or_saved_by_user(user=user)

    if current_user is not None:
        return user_decks.annotate(
            is_saved=Exists(current_user.saved_decks.filter(pk=OuterRef("pk")))
        )
    return user_decks


def get_deck_created_or_saved_by_user(deck_id, user):
    """
    Возвращает колоду если она создана или сохранена пользоватем.
    Иначе вернет 404.
    """
    deck = get_object_or_404(
        get_decks().filter(Q(author=user) | Q(saved_by=user)).distinct(), pk=deck_id
    )

    return deck


def get_deck_cards_with_saved_status(deck, user=None):
    """
    Возвращает карточки из колоды с флагом,
    который указывает сохранена ли карточка пользователем.
    """
    cards = (
        deck.cards.all()
        .select_related("author")
        .only("id", "question", "answer", "author__username")
    )

    if user is not None:
        return cards.annotate(
            is_saved=Exists(user.saved_cards.filter(pk=OuterRef("pk")))
        )

    return cards


def get_deck_cards(deck):
    """
    Возвращает все карточки из колоды.
    """
    cards = (
        deck.cards.all()
        .select_related("author")
        .only("id", "question", "answer", "author__username")
    )

    return cards


def filter_sort_paginate_decks(decks, query, sort_by, page_number, per_page=20):
    """
    Фильтрует, сортирует, пагинирует колоды. Возвращает page_obj.
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


def create_deck(author, **kwargs):
    """
    Создает и возвращает колоду с указанным автором.
    """
    cards = kwargs.pop("cards", None)
    if not cards:
        raise ValueError("В колоде должна быть хотя бы одна карточка")

    deck = Deck.objects.create(author=author, **kwargs)
    deck.cards.set(cards)

    return deck


def update_deck(deck, **kwargs):
    """
    Обновляет и возвращает колоду.
    """
    cards = kwargs.pop("cards", None)

    if not cards:
        raise ValueError("В колоде должна быть хотя бы одна карточка")

    for key, value in kwargs.items():
        setattr(deck, key, value)
    deck.save()

    deck.cards.set(cards)

    return deck


def delete_deck(deck):
    """Удаляет колоду."""
    deck.delete()


def toggle_deck_save_by_user(deck, user):
    """
    Переключает состояние сохранения колоды пользователем.
    Возвращает статус сохранения колоды и сообщение.
    """
    if deck.author == user:
        return False, "Вы автор этой колоды"

    if deck.is_saved:
        user.saved_decks.remove(deck)
        return False, "Колода удалена из вашего профиля"
    else:
        user.saved_decks.add(deck)
        return True, "Колода сохранена в ваш профиль"


def toggle_deck_study_by_user(deck, user):
    """Переключает состояние изучения колоды пользователем."""
    deck_progress = repetition_services.get_user_deck_progress(deck, user)

    if deck_progress.exists():
        deck_progress.delete()
        return False, f"Сброшен весь прогресс по колоде {deck.title}"
    else:
        repetition_services.create_deck_progress_for_user(deck, user)
        return True, f"Вы изучаете колоду {deck.title}"


def _generate_cards_data_for_export(cards):
    """
    Возвращает генератор, который
    формирует данные карточки для экспорта в txt формат.
    """
    for card in cards.iterator(chunk_size=1000):
        yield (
            f"#author_id: {card.author_id}\n"
            f"#card_id: {card.id}\n"
            f"{card.question}\t{card.answer}\n"
            "\n"
        )


def prepare_deck_for_export(deck):
    """
    Подготовливает колоду к экспорту.
    Возвращает кортеж (filename, cards_generator).
    """
    cards = get_deck_cards(deck)

    filename = f"{deck.title}.txt"
    cards_generator = _generate_cards_data_for_export(cards=cards)

    return filename, cards_generator


def get_decks_stats(user):
    decks = get_decks_created_or_saved_by_user(user=user)

    stats = decks.aggregate(
        total=Count("id", distinct=True),
        created=Count("id", filter=Q(author=user), distinct=True),
        saved=Count("id", filter=Q(saved_by=user), distinct=True),
        in_study=Count("id", filter=Q(card_progresses__learner=user), distinct=True),
    )

    return stats
