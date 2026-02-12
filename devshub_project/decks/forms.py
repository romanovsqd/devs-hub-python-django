from django import forms

from cards.card_services import get_all_user_created_or_saved_cards

from .models import CardSet


class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = ['title', 'cards']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['cards'].queryset = (
            get_all_user_created_or_saved_cards(self.user)
        )
