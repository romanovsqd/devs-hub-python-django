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

    def __init__(self, *args, **kwargs):
        cards_queryset = kwargs.pop('cards_queryset', None)
        super().__init__(*args, **kwargs)

        if cards_queryset is not None:
            self.fields['cards'].queryset = cards_queryset
