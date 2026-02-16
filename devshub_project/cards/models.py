from django.conf import settings
from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField


class Card(models.Model):
    question = models.CharField(max_length=255)
    answer = HTMLField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="created_cards", on_delete=models.CASCADE
    )
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="saved_cards", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["question"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.author.username} — {self.question}"

    def get_absolute_url(self):
        return reverse("card_detail", kwargs={"card_id": self.pk})
