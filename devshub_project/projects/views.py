from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from . import services
from .forms import ProjectForm


def project_list(request):
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    projects = services.filter_sort_projects(
        projects=services.get_projects(),
        query=query,
        sort_by=sort_by,
    )

    paginator = Paginator(projects, 20)
    page_obj = paginator.get_page(page_number)

    context = {
        "projects": page_obj,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "projects/project_list.html", context)


def project_detail(request, pk):
    project = services.get_project(project_id=pk)

    context = {
        "project": project,
    }

    return render(request, "projects/project_detail.html", context)


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)

        if form.is_valid():
            project = services.create_project(
                **form.cleaned_data,
                author=request.user,
            )
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm()

    context = {
        "form": form,
    }

    return render(request, "projects/project_form.html", context)


@login_required
def project_update(request, pk):
    project = services.get_project_created_by_user(project_id=pk, user=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)

        if form.is_valid():
            services.update_project(**form.cleaned_data, project=project)
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    context = {
        "form": form,
    }

    return render(request, "projects/project_form.html", context)


@login_required
def project_delete(request, pk):
    project = services.get_project_created_by_user(project_id=pk, user=request.user)

    if request.method == "POST":
        services.delete_project(project=project)
        return redirect("project_list")

    context = {
        "project": project,
    }

    return render(request, "projects/project_confirm_delete.html", context)
