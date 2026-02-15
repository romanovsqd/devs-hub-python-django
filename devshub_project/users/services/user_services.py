from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode

from users.tasks import send_confirmation_email_task

User = get_user_model()


def get_all_users():
    """Возврващет queryset всех пользователей."""
    return User.objects.all().select_related("codewars_profile")


def get_user_by_id(user_id):
    """Возвращает пользователя по id или 404."""
    return get_object_or_404(User, pk=user_id)


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


def update_user_email(base_url, old_email, new_email, user):
    """
    Обновляет email пользователя и отправляет новое письмо для подтверждения.
    """
    if not new_email:
        return

    if not user.email_verified:
        send_confirmation_email_task.delay(
            base_url=base_url, user_id=user.id, new_email=new_email
        )
        return

    if user.email_verified and new_email != old_email:
        user.email_verified = False
        user.save()
        send_confirmation_email_task.delay(
            base_url=base_url, user_id=user.id, new_email=new_email
        )
        return


def confirm_user_email(uidb64, token):
    """Подтверждает email пользователя по токену."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        return True
    return False
