from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Project, ProjectImage
from .forms import ProjectForm


@login_required
def project_list(request):
    query = request.GET.get('query', '')

    if query:
        projects = Project.objects.filter(title__icontains=query)
    else:
        projects = Project.objects.all()

    context = {
        'projects': projects
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    context = {
        'project': project
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
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
    else:
        form = ProjectForm()

    context = {
        'form': form,
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_update(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id,
        user=request.user
    )

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
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
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_delete(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id,
        user=request.user
    )

    if request.method == 'POST':
        project.delete()
        return redirect('projects:project_list')

    context = {
        'project': project
    }
    return render(request, 'projects/project_confirm_delete.html', context)
