from django import forms

from .models import Project


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            result = [single_file_clean(file, initial) for file in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProjectForm(forms.ModelForm):
    images = MultipleImageField(required=False)

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'repository_url',
            'live_url',
            'cover_image',
        ]
