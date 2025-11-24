from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    username = forms.CharField(
        max_length=150,
        required=True,
        label='Логин',
        help_text=''
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='пароль',
        help_text='',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Подтвердите пароль',
        help_text=''
    )
