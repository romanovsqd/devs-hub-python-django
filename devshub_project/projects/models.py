from django.conf import settings
from django.db import models
from django.urls import reverse


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    repository_url = models.URLField(max_length=255, blank=True)
    live_url = models.URLField(max_length=255, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="projects", on_delete=models.CASCADE
    )
    cover_image = models.ImageField(
        upload_to="projects/covers/", max_length=255, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"project_id": self.pk})


class ProjectImage(models.Model):
    project = models.ForeignKey(
        "Project", related_name="images", on_delete=models.CASCADE
    )
    file = models.ImageField(upload_to="projects/images/", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.project.title}"
