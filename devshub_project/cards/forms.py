from django import forms

from . import card_services

from .models import Card, CardSet


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['question', 'answer']


class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = ['title', 'cards']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['cards'].queryset = (
            card_services.get_all_user_created_or_saved_cards(self.user)
        )
