from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from . import services
from .forms import ProjectForm


@login_required
def project_list(request):
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    projects = services.filter_sort_paginate_projects(
        projects=services.get_all_projects(),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=10,
    )

    context = {
        "projects": projects,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "projects/project_list.html", context)


@login_required
def project_detail(request, project_id):
    project = services.get_project_by_id(project_id=project_id)

    context = {
        "project": project,
    }

    return render(request, "projects/project_detail.html", context)


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.author = request.user
        project.save()

        services.create_images_for_project(
            project=project, images=form.cleaned_data.get("images")
        )

        return redirect(project.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, "projects/project_form.html", context)


@login_required
def project_update(request, project_id):
    project = services.get_user_created_project_by_id(
        project_id=project_id, user=request.user
    )

    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)

    if form.is_valid():
        new_images = form.cleaned_data.get("images")
        project = form.save()

        services.update_project_images(project=project, new_images=new_images)

        return redirect(project.get_absolute_url())

    context = {
        "form": form,
    }

    return render(request, "projects/project_form.html", context)


@login_required
def project_delete(request, project_id):
    project = services.get_user_created_project_by_id(
        project_id=project_id, user=request.user
    )

    if request.method == "POST":
        project.delete()
        return redirect("project_list")

    context = {
        "project": project,
    }

    return render(request, "projects/project_confirm_delete.html", context)
