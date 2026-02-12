from django.conf import settings
from django.db import models
from django.urls import reverse


class Card(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_cards',
        on_delete=models.CASCADE
    )
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='saved_cards',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('card_detail', kwargs={'card_id': self.pk})


class CardSet(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_cardsets',
        on_delete=models.CASCADE
    )
    cards = models.ManyToManyField(
        'Card',
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
