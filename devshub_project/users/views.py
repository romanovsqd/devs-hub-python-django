from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView
)
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import requests

from cards.models import CardSetProgress
from cards import card_services, cardset_services
from . import user_services
from projects import project_services
from .models import CodewarsProfile

from .forms import LoginForm, RegisterForm, UserForm


User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect('users:profile_detail')

    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        user = authenticate(
            request,
            username=user.username,
            password=form.cleaned_data['password1']
        )
        login(request, user)

        return redirect('users:profile_detail')

    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


class LoginUserView(LoginView):
    authentication_form = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)


class UserPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)


class UserPasswordResetDoneView(PasswordResetDoneView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile_detail')
        return super().dispatch(request, *args, **kwargs)


@login_required
def user_list(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    users = user_services.get_all_users()

    users = user_services.filter_sort_paginate_users(
        users,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'users': users,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'users/users/user_list.html', context)


@login_required
def user_detail(request, user_id):
    user = user_services.get_user_by_id(user_id)

    if user == request.user:
        return redirect('users:profile_detail')

    cards_stats = card_services.get_user_cards_stats(user)

    cardsets_stats = cardset_services.get_user_cardsets_stats(user)

    projects_stats = project_services.get_user_project_stats(user)

    context = {
        'user': user,
        'cards_stats': cards_stats,
        'cardsets_stats': cardsets_stats,
        'projects_stats': projects_stats,
    }

    return render(request, 'users/users/user_detail.html', context)


@login_required
def user_cards(request, user_id):
    user = user_services.get_user_by_id(user_id)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    user_cards = card_services.get_all_user_created_or_saved_cards(user)

    user_cards = card_services.filter_sort_paginate_cards(
        user_cards,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'user': user,
        'user_cards': user_cards,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'users/users/user_cards.html', context)


@login_required
def user_cardsets(request, user_id):
    user = user_services.get_user_by_id(user_id)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    user_cardsets = (
        cardset_services.get_all_user_created_or_saved_cardsets(user)
    )

    user_cardsets = cardset_services.filter_sort_paginate_cardsets(
        user_cardsets,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'user': user,
        'user_cardsets': user_cardsets,
        'query': query,
        'sort_by': sort_by,
    }

    return render(request, 'users/users/user_cardsets.html', context)


@login_required
def user_projects(request, user_id):
    user = user_services.get_user_by_id(user_id)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    user_projects = project_services.get_all_user_created_projects(user)
    user_projects = project_services.filter_sort_paginate_projects(
        user_projects,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'user': user,
        'user_projects': user_projects,
        'query': query,
        'sort_by': sort_by,
    }

    return render(request, 'users/users/user_projects.html', context)


@login_required
def profile_detail(request):
    user = request.user

    cards_stats = card_services.get_user_cards_stats(user)

    cardsets_stats = cardset_services.get_user_cardsets_stats(user)

    projects_stats = project_services.get_user_project_stats(user)

    if hasattr(user, 'codewars_profile'):
        codewars_stats = user.codewars_profile
    else:
        codewars_stats = None

    context = {
        'user': user,
        'cards_stats': cards_stats,
        'cardsets_stats': cardsets_stats,
        'projects_stats': projects_stats,
        'codewars_stats': codewars_stats,
    }

    return render(request, 'users/profile/profile_detail.html', context)


@login_required
def profile_update(request):
    user = request.user

    user_form = UserForm(
        request.POST or None, request.FILES or None, instance=user
    )
    password_form = PasswordChangeForm(user, request.POST or None)

    if 'update_profile' in request.POST:
        old_email = user.email

        if user_form.is_valid():
            user_email = user_form.cleaned_data['email']
            codewars_username = user_form.cleaned_data['codewars_username']

            if user_email != old_email:
                user.email_verified = False

            if user_email and user_email != old_email:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                link = request.build_absolute_uri(
                    reverse(
                        'users:confirm_email',
                        kwargs={
                            'uidb64': uid,
                            'token': token
                        }
                    )
                )

                send_mail(
                    'Подтверждение почты',
                    f'Перейдите по ссылке:\n{link}',
                    'devs-hub@mail.com',
                    [user_email],
                )

            if codewars_username:
                url = f'https://www.codewars.com/api/v1/users/{codewars_username}'
                response = requests.get(url)

                print(response.status_code)

                if response.status_code == 200:
                    data = response.json()
                    CodewarsProfile.objects.update_or_create(
                        user=user,
                        defaults={
                            'username': data['username'],
                            'honor': data['honor'],
                            'leaderboard_position': data['leaderboardPosition'],
                            'languages': list(data['ranks']['languages'].keys()),
                            'total_completed_katas': data['codeChallenges']['totalCompleted']
                        }
                    )

            user_form.save()

            return redirect('users:profile_update')

    elif 'change_password' in request.POST:

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('users:profile_update')

    return render(request, 'users/profile/profile_form.html', {
        'user_form': user_form,
        'password_form': password_form,
    })


def confirm_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        return redirect('users:profile_update')

    return redirect('users:profile_update')


@login_required
def profile_cards(request):
    user = request.user
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    user_cards = card_services.get_all_user_created_or_saved_cards(user)

    user_cards = card_services.filter_sort_paginate_cards(
        user_cards,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'user': user,
        'user_cards': user_cards,
        'query': query,
        'sort_by': sort_by,
    }

    return render(request, 'users/profile/profile_cards.html', context)


@login_required
def profile_cardsets(request):
    user = request.user
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    user_cardsets = (
        cardset_services.get_all_user_created_or_saved_cardsets(user)
    )

    user_cardsets = cardset_services.filter_sort_paginate_cardsets(
        user_cardsets,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    studying_cardsets_ids = CardSetProgress.objects.filter(
        learner=user,
    ).values_list('cardset_id', flat=True)

    context = {
        'user': user,
        'user_cardsets': user_cardsets,
        'query': query,
        'sort_by': sort_by,
        'studying_cardsets_ids': studying_cardsets_ids,
    }

    return render(request, 'users/profile/profile_cardsets.html', context)


@login_required
def profile_projects(request):
    user = request.user
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)

    user_projects = project_services.get_all_user_created_projects(user)
    user_projects = project_services.filter_sort_paginate_projects(
        user_projects,
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20
    )

    context = {
        'user': user,
        'user_projects': user_projects,
        'query': query,
        'sort_by': sort_by,
    }
    return render(request, 'users/profile/profile_projects.html', context)
