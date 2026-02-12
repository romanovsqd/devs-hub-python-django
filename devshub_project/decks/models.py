from django.conf import settings
from django.db import models
from django.urls import reverse


class CardSet(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_cardsets',
        on_delete=models.CASCADE
    )
    cards = models.ManyToManyField(
        'cards.Card',
        related_name='cardsets',
        blank=True
    )
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='saved_cardsets',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'cardset_detail', kwargs={'cardset_id': self.pk}
        )
