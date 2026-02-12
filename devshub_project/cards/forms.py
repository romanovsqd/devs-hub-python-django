from django import forms

from . import card_services

from .models import Card


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['question', 'answer']
