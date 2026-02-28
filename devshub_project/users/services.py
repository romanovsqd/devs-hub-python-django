from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode

from .models import CodewarsProfile
from .tasks import (
    create_or_update_user_codewars_profile_task,
    send_confirmation_email_task,
)

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


def get_user(user_id):
    """
    Возвращает пользователя.
    Если пользователь не найден, вернет 404.
    """
    return get_object_or_404(get_users(), pk=user_id)


def get_user_with_codewars_profile(user_id):
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
        pk=user_id,
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


def _update_user_email(user, old_email, email, base_url):
    """
    Обновляет email пользователя и отправляет письмо для подтверждения.
    """
    if not email:
        user.email = email
        user.email_verified = False
        return False

    if email == old_email and user.email_verified:
        return False

    if email != old_email:
        user.email = email
        user.email_verified = False

    send_confirmation_email_task.delay(
        user_id=user.pk,
        email=email,
        base_url=base_url,
    )
    return True


def _update_codewars_username(user, old_codewars_username, codewars_username):
    """
    Обновляет данные codewars аккаута пользователя.
    """
    if not codewars_username:
        user.codewars_username = codewars_username
        CodewarsProfile.objects.filter(user=user).delete()
        return

    if codewars_username == old_codewars_username:
        return

    user.codewars_username = codewars_username
    create_or_update_user_codewars_profile_task.delay(
        user_id=user.pk, codewars_username=codewars_username
    )


def update_user(user, old_email, old_codewars_username, base_url, **kwargs):
    """
    Обновляет данные пользователя.
    """
    email = kwargs.pop("email", None)
    codewars_username = kwargs.pop("codewars_username", None)

    email_send = _update_user_email(
        user=user, old_email=old_email, email=email, base_url=base_url
    )

    _update_codewars_username(
        user=user,
        old_codewars_username=old_codewars_username,
        codewars_username=codewars_username,
    )

    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()

    return user, email_send


def confirm_user_email(uidb64, token):
    """Подтверждает email пользователя по токену."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return False

    if not default_token_generator.check_token(user, token):
        return False

    user.email_verified = True
    user.save()
    return True
