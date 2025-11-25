from django.conf import settings
from django.db import models


class Card(models.Model):
    front = models.CharField(max_length=255)
    back = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cards',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['front']),
        ]

    def __str__(self):
        return self.front
