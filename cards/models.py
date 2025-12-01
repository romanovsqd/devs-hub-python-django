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
        indexes = [
            models.Index(fields=['question']),
        ]

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('cards:card_detail', kwargs={'card_id': self.pk})


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
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'cardsets:cardset_detail', kwargs={'cardset_id': self.pk}
        )


class CardSetProgress(models.Model):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cardset_progresses',
        on_delete=models.CASCADE
    )
    cardset = models.ForeignKey(
        'CardSet',
        related_name='card_progresses',
        on_delete=models.CASCADE
    )
    card = models.ForeignKey(
        'Card',
        related_name='cardset_progresses',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['learner', 'cardset', 'card']
        indexes = [
            models.Index(fields=['learner']),
        ]

    def __str__(self):
        return f'{self.learner} – {self.card}'
