from django.conf import settings
from django.db import models
from django.urls import reverse


class Card(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cards',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['question']),
        ]

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('cards:card_detail', kwargs={'card_id': self.pk})
