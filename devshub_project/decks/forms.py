from django import forms

from cards.services import get_all_user_created_or_saved_cards

from .models import Deck


class DeckForm(forms.ModelForm):
    required_css_class = "required"

    class Meta:
        model = Deck
        fields = ["title", "cards"]
        labels = {
            "title": "Название колоды",
            "cards": "Карточки",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md flex-6 shadow",
                    "placeholder": "Основные структуры данных в Python",
                },
            ),
            "cards": forms.SelectMultiple(
                attrs={
                    "class": (
                        "w-full border-gray-300 rounded-md"
                        "flex-6 shadow min-h-96 resize-y"
                    ),
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields["cards"].queryset = get_all_user_created_or_saved_cards(self.user)
