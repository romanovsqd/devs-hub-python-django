from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    specialization = models.CharField(max_length=50, blank=True)
    primary_skill = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['username']
        indexes = [
            models.Index(fields=['username']),
        ]

    def get_absolute_url(self):
        return reverse('users:user_detail', kwargs={'user_id': self.pk})

    def __str__(self):
        return f'{self.username} ({self.specialization})'
