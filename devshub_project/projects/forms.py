from django import forms
from tinymce.widgets import TinyMCE

from .models import Project


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            result = [single_file_clean(file, initial) for file in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProjectForm(forms.ModelForm):
    required_css_class = "required"
    images = MultipleImageField(
        required=False,
        label="Изображения проекта",
        widget=MultipleFileInput(
            attrs={
                "class": (
                    "ml-2 rounded-full text-sm text-gray-500 file:mr-4 file:py-2 "
                    "file:px-4 file:rounded-full file:border-0 file:text-sm "
                    "file:font-semibold file:bg-blue-50 file:text-blue-700 "
                    "hover:file:bg-blue-100 file:cursor-pointer cursor-pointer "
                    "file:transition-colors"
                )
            }
        ),
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "repository_url",
            "live_url",
            "cover_image",
        ]
        labels = {
            "title": "Название проекта",
            "description": "Описание проекта",
            "repository_url": "Ссылка на репозиторий",
            "live_url": "Ссылка на проект",
            "cover_image": "Обложка проекта",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "Чат на FastAPI + WebSocket",
                },
            ),
            "description": TinyMCE(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow min-h-64",
                    "placeholder": (
                        "Realtime чат с комнатами и историей сообщений на FastAPI "
                        "с использованием WebSocket..."
                    ),
                }
            ),
            "repository_url": forms.URLInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "Ссылка на GitHub репозиторий",
                },
            ),
            "live_url": forms.URLInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "Ссылка на Ваш проект",
                },
            ),
            "cover_image": forms.FileInput(
                attrs={
                    "class": (
                        "ml-2 rounded-full text-sm text-gray-500 file:mr-4 file:py-2 "
                        "file:px-4 file:rounded-full file:border-0 file:text-sm "
                        "file:font-semibold file:bg-blue-50 file:text-blue-700 "
                        "hover:file:bg-blue-100 file:cursor-pointer cursor-pointer "
                        "file:transition-colors"
                    )
                },
            ),
        }
