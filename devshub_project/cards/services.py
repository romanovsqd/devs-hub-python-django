from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404

from core.utils import clean_html

from .models import Card


def get_cards():
    """
    Возвращает queryset всех карточек.
    """
    return (
        Card.objects.all()
        .select_related("author")
        .only(
            "id", "question", "answer", "created_at", "updated_at", "author__username"
        )
    )


def get_cards_with_saved_status(user=None):
    """
    Возвращает queryset карточек с флагом,
    который указывает сохранена ли карточка пользователем.
    """
    cards = get_cards()

    if user is not None:
        return cards.annotate(
            is_saved=Exists(user.saved_cards.filter(pk=OuterRef("pk")))
        )

    return cards


def get_card_with_saved_status(card_id, user=None):
    """
    Возвращает карточку с флагом,
    который указывает сохранена ли карточка пользователем.
    """
    card = get_object_or_404(get_cards_with_saved_status(user=user), pk=card_id)

    return card


def get_card_created_by_user(card_id, user):
    """
    Возвращает карточку если она создана пользователем.
    Если пользователь не является автором, или
    если карточки не существует, вернет 404.
    """
    card = get_object_or_404(Card.objects.filter(author=user), pk=card_id)
    return card


def get_cards_created_or_saved_by_user(user):
    """
    Возвращает queryset карточек,
    которые созданы или сохранены пользователем.
    """
    cards = get_cards().filter(Q(author=user) | Q(saved_by=user)).distinct()
    return cards


def get_user_cards_with_saved_status(user, current_user):
    """
    Возвращает карточки созданные или сохраненные пользователем с флагом,
    который указывает сохранена ли карточка текущим пользователем.
    """
    user_cards = get_cards_created_or_saved_by_user(user=user)

    if current_user is not None:
        return user_cards.annotate(
            is_saved=Exists(current_user.saved_cards.filter(pk=OuterRef("pk")))
        )
    return user_cards


def get_card_created_or_saved_by_user(card_id, user):
    """
    Возвращает карточку если она создана или сохранена пользователем.
    Иначе вернет 404.
    """
    card = get_object_or_404(
        get_cards().filter(Q(author=user) | Q(saved_by=user)).distinct(), pk=card_id
    )

    return card


def filter_sort_paginate_cards(cards, query, sort_by, page_number, per_page=20):
    """
    Фильтрует, сортирует, пагинирует карточки. Возвращает page_obj.
    """
    if query:
        cards = cards.filter(question__icontains=query)

    if sort_by == "newest":
        cards = cards.order_by("-created_at")
    elif sort_by == "oldest":
        cards = cards.order_by("created_at")

    paginator = Paginator(cards, per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj


def create_card(question, answer, author, **kwargs):
    """
    Создает и возвращает карточку с указанным автором.
    Очищает question и answer от вредоносного HTML.
    """
    return Card.objects.create(
        question=clean_html(question),
        answer=clean_html(answer),
        author=author,
        **kwargs,
    )


def update_card(card, **kwargs):
    """
    Обновляет и возвращает карточку.
    Очищает question и answer от вредносного HTML.
    """
    question = kwargs.pop("question", None)
    answer = kwargs.pop("answer", None)

    if question:
        card.question = clean_html(question)
    if answer:
        card.answer = clean_html(answer)

    for key, value in kwargs.items():
        setattr(card, key, value)
    card.save()

    return card


def delete_card(card):
    """Удаляет карточку."""
    card.delete()


def toggle_card_save_by_user(card, user):
    """
    Переключает состояние сохранения карточки пользователем.
    Возвращает статус сохранения карточки и сообщение.
    """
    if card.author == user:
        return False, "Вы автор этой карточки"

    if card.is_saved:
        user.saved_cards.remove(card)
        return False, "Карточка удалена из вашего профиля"
    else:
        user.saved_cards.add(card)
        return True, "Карточка сохранена в ваш профиль"


def generate_card_data_for_export(card):
    """
    Формирует данные карточки для экспорта в txt формат.
    Возвращает кортеж (filename, content).
    """
    filename = f"{card.question}.txt"

    content = (
        f"#author_id: {card.author.id}\n"
        f"#card_id: {card.id}\n"
        f"{card.question}\t"
        f"{card.answer}\n"
    )
    return filename, content


def get_cards_stats(user):
    """
    Возвращает словарь со статистикой карточек для пользователя.
    """
    cards = get_cards_created_or_saved_by_user(user=user)

    stats = cards.aggregate(
        total=Count("id", distinct=True),
        created=Count("id", filter=Q(author=user), distinct=True),
        saved=Count("id", filter=Q(saved_by=user), distinct=True),
        in_study=Count("id", filter=Q(deck_progresses__learner=user), distinct=True),
    )

    return stats
