from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

User = get_user_model()


def get_all_users():
    """Возврващет queryset всех пользователей."""
    return User.objects.all()


def get_user_by_id(user_id):
    """Возвращает пользователя по id или 404."""
    return get_object_or_404(User, pk=user_id)


def filter_sort_paginate_users(
    users, query, sort_by, page_number, per_page=20
):
    """Фильтрует, сортирует, пагинирует пользователей. Возвращает page_obj."""
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(primary_skill__icontains=query)
            | Q(specialization__icontains=query)
        )

    if sort_by == 'username_asc':
        users = users.order_by('username')
    elif sort_by == 'username_desc':
        users = users.order_by('-username')

    paginator = Paginator(users, per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj


def update_user_email(base_url, old_email, new_email, user):
    """
    Обновляет email пользователя и отправляет новое письмо для подтверждения.
    """
    if not new_email:
        return

    if new_email != old_email:
        user.email_verified = False
        user.save()
        _send_confirmation_email(base_url, user)


def _send_confirmation_email(base_url, user):
    """
    Генерирует ссылку с токеном и отправляет письмо для подтверждение почты.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirm_url = reverse(
            'users:confirm_email',
            kwargs={
                'uidb64': uid,
                'token': token
            }
        )
    confirm_link = f'{base_url[:-1]}{confirm_url}'

    send_mail(
        'Подтверждение почты',
        f'Перейдите по ссылке:\n{confirm_link}',
        'devs-hub@mail.com',
        [user.email],
    )


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
