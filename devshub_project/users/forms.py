from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)
from django.template.loader import render_to_string

from .tasks import send_reset_email_task

User = get_user_model()


class RegisterForm(UserCreationForm):
    required_css_class = "required"

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "w-full border-gray-300 rounded-md shadow"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": "Введите новый пароль",
                "class": "w-full border-gray-300 rounded-md shadow",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": "Подтвердите новый пароль",
                "class": "w-full border-gray-300 rounded-md shadow",
            }
        )

    def clean_username(self):
        username = super().clean_username()

        if User.objects.filter(email=username).exists():
            raise forms.ValidationError("Логин уже занят")

        return username


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "placeholder": "username или email",
                "class": "w-full border-gray-300 rounded-md shadow mb-2",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "placeholder": "Пароль",
                "class": "w-full border-gray-300 rounded-md shadow mb-2",
            }
        )


class UserForm(UserChangeForm):
    password = None
    required_css_class = "required"

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "specialization",
            "skills",
            "codewars_username",
            "avatar",
        ]
        labels = {
            "username": "Имя профиля",
            "email": "email",
            "specialization": "Направление",
            "skills": "Навыки",
            "codewars_username": "codewars аккаунт",
            "avatar": "Аватар профиля",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "Ваш username",
                    "autofocus": True,
                },
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "example@mail.com",
                },
            ),
            "specialization": forms.TextInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "Backend разработчик",
                },
            ),
            "skills": forms.TextInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "python, docker, redis, celery, rabbitmq ...",
                },
            ),
            "codewars_username": forms.TextInput(
                attrs={
                    "class": "w-full border-gray-300 rounded-md shadow",
                    "placeholder": "Ваш username на codewars",
                },
            ),
            "avatar": forms.FileInput(
                attrs={
                    "class": (
                        "ml-2 rounded-full text-sm text-gray-500 file:mr-4 file:py-2 "
                        "file:px-4 file:rounded-full file:border-0 file:text-sm "
                        "file:font-semibold file:bg-blue-50 file:text-blue-700 "
                        "hover:file:bg-blue-100 hover:file:bg-blue-100 "
                        "file:cursor-pointer cursor-pointer file:transition-colors "
                    )
                },
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]

        if email:
            users_with_same_email = User.objects.filter(email=email).exclude(
                pk=self.instance.pk
            )
            if users_with_same_email.exists():
                raise forms.ValidationError("Пользователь с таким email уже существует")

        return email


class UserPasswordChangeForm(PasswordChangeForm):
    required_css_class = "required"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "w-full border-gray-300 rounded-md shadow"

        self.fields["old_password"].label = "Текущий пароль"
        self.fields["old_password"].widget.attrs.update(
            {"placeholder": "Введите текущий пароль"}
        )
        self.fields["new_password1"].widget.attrs.update(
            {"placeholder": "Введите новый пароль"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"placeholder": "Подтвердите новый пароль"}
        )


class UserPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email=None,
        to_email=None,
        html_email_template_name=None,
    ):

        subject = render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())

        message = render_to_string(email_template_name, context)

        send_reset_email_task.delay(
            subject=subject,
            message=message,
            email=to_email,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "Ваш email",
                "class": "w-full border-gray-300 rounded-md shadow",
            }
        )


class UserSetPasswordForm(SetPasswordForm):
    required_css_class = "required"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "w-full border-gray-300 rounded-md shadow"

        self.fields["new_password1"].widget.attrs.update(
            {"placeholder": "Введите новый пароль"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"placeholder": "Подтвердите новый пароль"}
        )
