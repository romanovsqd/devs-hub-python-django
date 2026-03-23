from django.db.models import Count
from django.shortcuts import get_object_or_404

from core.utils import clean_html

from .models import Project, ProjectImage


def get_projects():
    """
    Возвращает queryset всех проектов.
    """
    return (
        Project.objects.all()
        .select_related("author")
        .only(
            "id",
            "title",
            "description",
            "repository_url",
            "live_url",
            "cover_image",
            "created_at",
            "updated_at",
            "author__username",
        )
    )


def get_project(project_id):
    """
    Возвращает проект.
    """
    project = get_object_or_404(
        get_projects().prefetch_related("images"), pk=project_id
    )

    return project


def get_projects_created_by_user(user):
    return get_projects().filter(author=user)


def get_project_created_by_user(project_id, user):
    """
    Возвращает проект если он создан пользователем.
    Если пользователь не является автором, или
    если проекта не существует, вернет 404.
    """
    return get_object_or_404(Project.objects.filter(author=user), pk=project_id)


def filter_sort_projects(projects, query, sort_by):
    """Фильтрует, сортирует, пагинирует проекты. Возвращает page_obj."""
    if query:
        projects = projects.filter(title__icontains=query)

    if sort_by == "newest":
        projects = projects.order_by("-created_at")
    elif sort_by == "oldest":
        projects = projects.order_by("created_at")

    return projects


def _create_project_images(project, images):
    """
    Создает изображения для указанного проекта.
    """
    ProjectImage.objects.bulk_create(
        [ProjectImage(project=project, file=image) for image in images]
    )


def _update_project_images(project, images):
    """
    Создает новые изображения для указанного проекта
    и удаляет старые.
    """
    for image in project.images.all():
        image.file.delete()
    project.images.all().delete()

    _create_project_images(project, images)


def create_project(author, **kwargs):
    """
    Создает и возвращает проект с указанным автором.
    Очищает description от вредоносного HTML.
    """
    description = kwargs.pop("description")
    images = kwargs.pop("images", None)

    project = Project.objects.create(
        author=author,
        description=clean_html(description),
        **kwargs,
    )

    if images:
        _create_project_images(project=project, images=images)

    return project


def update_project(project, **kwargs):
    """
    Обновляет и возвращает проект.
    Очищает description от вредносного HTML.
    """
    description = kwargs.pop("description", None)
    images = kwargs.pop("images", None)

    if description:
        project.description = clean_html(description)

    for key, value in kwargs.items():
        setattr(project, key, value)
    project.save()

    if images:
        _update_project_images(project=project, images=images)

    return project


def delete_project(project):
    """Удаляет проект."""
    project.delete()


def get_projects_stats(user):
    projects = get_projects().filter(author=user)

    stats = projects.aggregate(
        total=Count("id"),
    )

    return stats
