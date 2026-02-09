from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Project


def get_all_projects():
    """Возврващет queryset всех проектов."""
    return Project.objects.all()


def get_project_by_id(project_id):
    """Возвращает проект по id или 404."""
    return get_object_or_404(Project, pk=project_id)


def get_user_created_project_by_id(project_id, user):
    """Возвращает проект по id, если он создан пользователем, иначе 404."""
    return get_object_or_404(
        Project,
        pk=project_id,
        user=user
    )


def filter_sort_paginate_projects(
    projects, query, sort_by, page_number, per_page=20
):
    """Фильтрует, сортирует, пагинирует проекты. Возвращает page_obj."""
    if query:
        projects = Project.objects.filter(title__icontains=query)

    if sort_by == 'newest':
        projects = projects.order_by('-created_at')
    elif sort_by == 'oldest':
        projects = projects.order_by('created_at')

    paginator = Paginator(projects, per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj
