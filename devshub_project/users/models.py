from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    specialization = models.CharField(max_length=50, blank=True)
    primary_skill = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    codewars_username = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['username']
        indexes = [
            models.Index(fields=['username']),
        ]

    def get_absolute_url(self):
        return reverse('user_detail', kwargs={'user_id': self.pk})

    def __str__(self):
        return f'{self.username} ({self.specialization})'


class CodewarsProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='codewars_profile'
    )
    honor = models.PositiveIntegerField(default=0)
    leaderboard_position = models.PositiveIntegerField(default=0)
    languages = models.JSONField(default=list)
    total_completed_katas = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['honor']),
            models.Index(fields=['leaderboard_position']),
        ]

    def __str__(self):
        return (
            f'{self.user.username} — Codewars: {self.user.codewars_username}'
        )
