from django.contrib.auth import (
    authenticate,
    login,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView
)
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from cards import card_services, cardset_services, cardsetprogress_services
from .decorators import redirect_authenticated
from projects import project_services

from . import user_services, codewars_services
from .forms import LoginForm, RegisterForm, UserForm


@redirect_authenticated
def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        user = authenticate(
            request,
            username=user.username,
            password=form.cleaned_data['password1']
        )
        login(request, user)

        return redirect('users:user_detail', user_id=request.user.pk)

    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


class LoginUserView(LoginView):
    authentication_form = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:user_detail', user_id=request.user.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('users:user_detail', kwargs={
            'user_id': self.request.user.pk
            }
        )


class UserPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:user_detail', user_id=request.user.pk)
        return super().dispatch(request, *args, **kwargs)


class UserPasswordResetDoneView(PasswordResetDoneView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:user_detail', user_id=request.user.pk)
        return super().dispatch(request, *args, **kwargs)


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:user_detail', user_id=request.user.pk)
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

    cards_stats = card_services.get_user_cards_stats(user)

    cardsets_stats = cardset_services.get_user_cardsets_stats(user)

    projects_stats = project_services.get_user_project_stats(user)

    codewars_stats = codewars_services.get_user_codewars_stats(user)

    is_owner = user == request.user

    context = {
        'user': user,
        'cards_stats': cards_stats,
        'cardsets_stats': cardsets_stats,
        'projects_stats': projects_stats,
        'codewars_stats': codewars_stats,
        'is_owner': is_owner,
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

    is_owner = user == request.user

    context = {
        'user': user,
        'user_cards': user_cards,
        'query': query,
        'sort_by': sort_by,
        'is_owner': is_owner,
    }
    return render(request, 'users/users/user_cards.html', context)


@login_required
def user_cardsets(request, user_id):
    user = user_services.get_user_by_id(user_id)
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    page_number = request.GET.get('page', 1)
    studying_cardsets_ids = []

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

    is_owner = user == request.user

    if is_owner:
        studying_cardsets_ids = (
            cardsetprogress_services.get_user_studying_cardsets_ids(user)
        )

    context = {
        'user': user,
        'user_cardsets': user_cardsets,
        'studying_cardsets_ids': studying_cardsets_ids,
        'query': query,
        'sort_by': sort_by,
        'is_owner': is_owner
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

    is_owner = user == request.user

    context = {
        'user': user,
        'user_projects': user_projects,
        'query': query,
        'sort_by': sort_by,
        'is_owner': is_owner,
    }

    return render(request, 'users/users/user_projects.html', context)


@login_required
def user_update(request, user_id):
    user = user_services.get_user_by_id(user_id)

    if user != request.user:
        return redirect(user.get_absolute_url())

    user_form = UserForm(
        request.POST or None, request.FILES or None, instance=user
    )
    password_form = PasswordChangeForm(user, request.POST or None)

    if 'update_user' in request.POST:
        old_email = user.email
        old_codewars_username = user.codewars_username

        if user_form.is_valid():
            cleaned_data = user_form.cleaned_data
            email = cleaned_data.get('email', None)
            codewars_username = cleaned_data.get('codewars_username', None)

            user_services.update_user_email(
                base_url=request.build_absolute_uri('/'),
                old_email=old_email,
                new_email=email,
                user=user,
            )

            codewars_services.create_or_update_user_codears_profile(
                user=user,
                codewars_username=codewars_username,
                old_codewars_username=old_codewars_username,
            )

            user_form.save()
            return redirect('users:user_update', user_id=user.pk)

    elif 'change_password' in request.POST:
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('users:user_update', user_id=user.pk)

    return render(request, 'users/users/user_form.html', {
        'user_form': user_form,
        'password_form': password_form,
    })


def confirm_email(request, uidb64, token):
    user_services.confirm_user_email(
        uidb64=uidb64,
        token=token
    )
    return redirect('users:user_update', user_id=request.user.pk)
