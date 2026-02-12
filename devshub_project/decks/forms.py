from django import forms

from cards.services import get_all_user_created_or_saved_cards

from .models import Deck


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ["title", "cards"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields["cards"].queryset = get_all_user_created_or_saved_cards(self.user)
