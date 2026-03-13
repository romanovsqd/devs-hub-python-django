from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import CodewarsProfile
from .tasks import create_or_update_user_codewars_profile_task

User = get_user_model()


def get_users():
    """Возвращает queryset пользователей"""
    return User.objects.all().only(
        "id",
        "username",
        "specialization",
        "skills",
        "avatar",
        "codewars_username",
    )


def get_user(username):
    """
    Возвращает пользователя.
    Если пользователь не найден, вернет 404.
    """
    return get_object_or_404(get_users(), username=username)


def get_user_with_codewars_profile(username):
    """
    Возвращает пользователя с codewars_profile.
    Если пользователь не найден, вернет 404.
    """
    return get_object_or_404(
        get_users()
        .select_related("codewars_profile")
        .only(
            "id",
            "username",
            "specialization",
            "skills",
            "avatar",
            "codewars_username",
            "codewars_profile",
        ),
        username=username,
    )


def filter_sort_paginate_users(users, query, sort_by, page_number, per_page=20):
    """Фильтрует, сортирует, пагинирует пользователей. Возвращает page_obj."""
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(skills__icontains=query)
            | Q(specialization__icontains=query)
        )

    if sort_by == "newest":
        users = users.order_by("-date_joined")
    elif sort_by == "oldest":
        users = users.order_by("date_joined")

    paginator = Paginator(users, per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj


def create_user(username, password, **kwargs):
    """Создает нового пользователя."""
    kwargs.pop("password1", None)
    kwargs.pop("password2", None)

    return User.objects.create_user(
        username=username,
        password=password,
        **kwargs,
    )


def _update_codewars_username(user, codewars_username):
    """
    Обновляет данные codewars аккаута пользователя.
    """

    if not codewars_username:
        CodewarsProfile.objects.filter(user=user).delete()
        return

    user.codewars_username = codewars_username
    create_or_update_user_codewars_profile_task.delay(
        user_id=user.pk, codewars_username=codewars_username
    )


def update_user(user, **kwargs):
    """
    Обновляет данные пользователя.
    """
    codewars_username = kwargs.pop("codewars_username", None)
    password = kwargs.pop("password", None)

    _update_codewars_username(user=user, codewars_username=codewars_username)

    if password:
        user.set_password(password)

    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()

    return user
