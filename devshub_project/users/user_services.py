from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404

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
