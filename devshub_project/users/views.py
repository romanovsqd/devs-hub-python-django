from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from cards import services as card_services
from decks import services as deck_services
from projects import services as project_services
from repetitions import services as repetition_services

from . import services
from .decorators import redirect_authenticated
from .forms import (
    LoginForm,
    RegisterForm,
    UserForm,
    UserPasswordChangeForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
)


@redirect_authenticated
def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = services.create_user(
            **form.cleaned_data,
            password=form.cleaned_data["password1"],
        )
        user = authenticate(
            request,
            username=user.username,
            password=form.cleaned_data["password1"],
        )
        login(request, user)

        return redirect("user_detail", user_id=request.user.pk)

    context = {
        "form": form,
    }

    return render(request, "registration/register.html", context)


class LoginUserView(LoginView):
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse("user_detail", kwargs={"user_id": self.request.user.pk})


class UserPasswordResetView(PasswordResetView):
    success_url = reverse_lazy("password_reset_done")
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("password_reset_complete")
    form_class = UserSetPasswordForm


def user_list(request):
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    users = services.filter_sort_paginate_users(
        users=services.get_users(),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    context = {
        "users": users,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "users/user_list.html", context)


def user_detail(request, user_id):
    user = services.get_user_with_codewars_profile(user_id=user_id)
    cards_stats = card_services.get_cards_stats(user=user)
    decks_stats = deck_services.get_decks_stats(user=user)
    projects_stats = project_services.get_projects_stats(user=user)

    context = {
        "user": user,
        "cards_stats": cards_stats,
        "decks_stats": decks_stats,
        "projects_stats": projects_stats,
    }

    return render(request, "users/user_detail.html", context)


def user_cards(request, user_id):
    user = services.get_user(user_id=user_id)
    current_user = request.user if request.user.is_authenticated else None

    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    user_cards = card_services.filter_sort_paginate_cards(
        cards=card_services.get_user_cards_with_saved_status(
            user=user,
            current_user=current_user,
        ),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    context = {
        "user": user,
        "user_cards": user_cards,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "users/user_cards.html", context)


def user_decks(request, user_id):
    user = services.get_user(user_id=user_id)
    current_user = request.user if request.user.is_authenticated else None
    studying_decks_ids = repetition_services.get_studying_decks_ids(user=user)

    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    user_decks = deck_services.filter_sort_paginate_decks(
        decks=deck_services.get_user_decks_with_saved_status(
            user=user,
            current_user=current_user,
        ),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    context = {
        "user": user,
        "user_decks": user_decks,
        "studying_decks_ids": studying_decks_ids,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "users/user_decks.html", context)


def user_projects(request, user_id):
    user = services.get_user(user_id=user_id)

    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    user_projects = project_services.filter_sort_paginate_projects(
        projects=project_services.get_projects_created_by_user(user=user),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=10,
    )

    context = {
        "user": user,
        "user_projects": user_projects,
        "query": query,
        "sort_by": sort_by,
    }

    return render(request, "users/user_projects.html", context)


@login_required
def user_update(request, user_id):
    user = services.get_user(user_id=user_id)

    if user != request.user:
        return redirect(user.get_absolute_url())

    if request.method == "POST":

        if "update_user" in request.POST:
            user_form = UserForm(request.POST, request.FILES, instance=user)
            password_form = UserPasswordChangeForm(user)

            old_email = user.email
            old_codewars_username = user.codewars_username

            if user_form.is_valid():
                user, email_send = services.update_user(
                    **user_form.cleaned_data,
                    user=user,
                    old_email=old_email,
                    old_codewars_username=old_codewars_username,
                    base_url=request.build_absolute_uri("/"),
                )

                messages.success(request, "Данные профиля сохранены")
                if email_send:
                    messages.info(request, "Отправлено письмо для подтверждения почты")

                return redirect("user_update", user_id=user.pk)

        elif "change_password" in request.POST:
            user_form = UserForm(instance=user)
            password_form = UserPasswordChangeForm(user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                messages.success(request, "Пароль успешно изменен")

                return redirect("user_update", user_id=user.pk)

    else:
        user_form = UserForm(instance=user)
        password_form = UserPasswordChangeForm(user)

    context = {
        "user_form": user_form,
        "password_form": password_form,
    }

    return render(request, "users/user_form.html", context)


def confirm_email(request, uidb64, token):
    is_email_confirmed = services.confirm_user_email(uidb64=uidb64, token=token)

    if is_email_confirmed:
        messages.success(request, "Ваш email успешно подтвержден")
    return redirect("user_update", user_id=request.user.pk)
