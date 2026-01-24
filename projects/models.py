from django.conf import settings
from django.db import models
from django.urls import reverse


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    repository_url = models.URLField(max_length=255, blank=True)
    live_url = models.URLField(max_length=255, blank=True)
    cover_image = models.ImageField(
        upload_to='projects/covers/',
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'projects:project_detail', kwargs={'project_id': self.pk}
        )


class ProjectImage(models.Model):
    project = models.ForeignKey(
        'Project',
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='projects/images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Image for {self.project.title}'
