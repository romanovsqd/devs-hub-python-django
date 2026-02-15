from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    specialization = models.CharField(max_length=100, blank=True)
    skills = models.CharField(max_length=100, blank=True)
    email_verified = models.BooleanField(default=False)
    codewars_username = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/", max_length=255, blank=True, null=True
    )

    class Meta:
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["-date_joined"]),
        ]

    def get_absolute_url(self):
        return reverse("user_detail", kwargs={"user_id": self.pk})

    def __str__(self):
        return f"{self.username}"


class CodewarsProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="codewars_profile",
    )
    honor = models.PositiveIntegerField(default=0, blank=True, null=True)
    leaderboard_position = models.PositiveIntegerField(default=0, blank=True, null=True)
    languages = models.JSONField(default=list, blank=True, null=True)
    total_completed_katas = models.PositiveIntegerField(
        default=0, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["updated_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} — Codewars: {self.user.codewars_username}"
