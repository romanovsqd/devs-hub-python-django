from django import forms

from .models import Card


class CardForm(forms.ModelForm):
    required_css_class = "required"

    class Meta:
        model = Card
        fields = ["question", "answer"]
        labels = {
            "question": "Вопрос",
            "answer": "Ответ",
        }
        widgets = {
            "question": forms.TextInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "Что такое интерпретатор?",
                },
            ),
            "answer": forms.Textarea(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow min-h-64",
                    "placeholder": (
                        "Интерпретатор — это программа, которая читает "
                        "и выполняет код построчно."
                    ),
                    "cols": 0,
                    "rows": 0,
                }
            ),
        }
