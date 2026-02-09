from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from . import project_services

from .models import ProjectImage
from .forms import ProjectForm


@login_required
def project_list(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    projects = project_services.get_all_projects()

    projects = project_services.filter_sort_paginate_projects(
        projects,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'projects': projects,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, project_id):
    project = project_services.get_project_by_id(project_id)

    context = {
        'project': project
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.user = request.user
        project.save()

        images = form.cleaned_data.get('images')

        if images:
            ProjectImage.objects.bulk_create([
                ProjectImage(
                    project=project,
                    image=image
                )
                for image in images
            ])

        return redirect(project.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_update(request, project_id):
    project = project_services.get_user_created_project_by_id(
        project_id, request.user
    )

    form = ProjectForm(
        request.POST or None, request.FILES or None, instance=project
    )

    if form.is_valid():
        project = form.save()

        images = form.cleaned_data.get('images')

        if images:
            for img in project.images.all():
                img.image.delete(save=False)
                img.delete()

            ProjectImage.objects.bulk_create([
                ProjectImage(project=project, image=image)
                for image in images
            ])

        return redirect(project.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_delete(request, project_id):
    project = project_services.get_user_created_project_by_id(
        project_id, request.user
    )

    if request.method == 'POST':
        project.delete()
        return redirect('projects:project_list')

    context = {
        'project': project
    }
    return render(request, 'projects/project_confirm_delete.html', context)
