from django import forms

from .models import Card, CardSet


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['question', 'answer']


class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = ['title', 'cards']
