from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserChangeForm,
    UserCreationForm,
)
from django.template.loader import render_to_string

from .tasks import send_reset_email

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    username = forms.CharField(
        max_length=150, required=True, label="Логин", help_text=""
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput, label="пароль", help_text=""
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Подтвердите пароль", help_text=""
    )

    def clean_username(self):
        username = super().clean_username()

        if User.objects.filter(email=username).exists():
            raise forms.ValidationError("Логин уже занят")

        return username


class LoginForm(AuthenticationForm):
    class Mega:
        model = User
        fields = ["username", "password"]

    username = forms.CharField(
        max_length=150, required=True, label="Логин", help_text=""
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="пароль",
        help_text="",
    )


class UserForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "specialization",
            "primary_skill",
            "codewars_username",
            "avatar",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if email:
            users_with_same_email = User.objects.filter(email=email).exclude(
                pk=self.instance.pk
            )
            if users_with_same_email.exists():
                raise forms.ValidationError("Пользователь с таким email уже существует")

        return email


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

        send_reset_email.delay(
            subject=subject,
            message=message,
            email=to_email,
        )
