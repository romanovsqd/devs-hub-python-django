from django.conf import settings
from django.db import models
from django.utils import timezone


class CardSetProgress(models.Model):
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cardset_progresses',
        on_delete=models.CASCADE
    )
    cardset = models.ForeignKey(
        'cards.CardSet',
        related_name='progresses',
        on_delete=models.CASCADE
    )
    card = models.ForeignKey(
        'cards.Card',
        related_name='cardset_progresses',
        on_delete=models.CASCADE
    )
    repetitions = models.PositiveIntegerField(default=0)
    efactor = models.FloatField(default=2.5)
    interval = models.PositiveIntegerField(default=0)
    next_review_date = models.DateTimeField(default=timezone.now)
    last_review_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['learner', 'cardset', 'card']
        ordering = ['next_review_date']
        indexes = [
            models.Index(fields=['learner']),
            models.Index(fields=['next_review_date']),
        ]

    def __str__(self):
        return f'{self.learner} – {self.card}: {self.next_review_date}'
