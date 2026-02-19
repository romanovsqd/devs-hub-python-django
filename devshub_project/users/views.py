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
from repetitions import services as deckprogress_services

from .decorators import redirect_authenticated
from .forms import (
    LoginForm,
    RegisterForm,
    UserForm,
    UserPasswordChangeForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
)
from .services import codewars_services, user_services
from .tasks import create_or_update_user_codewars_profile_task


@redirect_authenticated
def register(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()
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


@login_required
def user_list(request):
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    users = user_services.filter_sort_paginate_users(
        users=user_services.get_all_users(),
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


@login_required
def user_detail(request, user_id):
    user = user_services.get_user_by_id(user_id=user_id)
    cards_stats = card_services.get_user_cards_stats(user=user)
    decks_stats = deck_services.get_user_decks_stats(user=user)
    projects_stats = project_services.get_user_project_stats(user=user)
    codewars_stats = codewars_services.get_user_codewars_stats(user=user)
    is_owner = user == request.user

    context = {
        "user": user,
        "cards_stats": cards_stats,
        "decks_stats": decks_stats,
        "projects_stats": projects_stats,
        "codewars_stats": codewars_stats,
        "is_owner": is_owner,
    }

    return render(request, "users/user_detail.html", context)


@login_required
def user_cards(request, user_id):
    user = user_services.get_user_by_id(user_id=user_id)
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    user_cards = card_services.filter_sort_paginate_cards(
        cards=card_services.get_all_user_created_or_saved_cards(user=user),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    is_owner = user == request.user

    context = {
        "user": user,
        "user_cards": user_cards,
        "query": query,
        "sort_by": sort_by,
        "is_owner": is_owner,
    }

    return render(request, "users/user_cards.html", context)


@login_required
def user_decks(request, user_id):
    user = user_services.get_user_by_id(user_id=user_id)
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    user_decks = deck_services.filter_sort_paginate_decks(
        decks=deck_services.get_all_user_created_or_saved_decks(user=user),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=20,
    )

    is_owner = user == request.user

    studying_decks_ids = (
        deckprogress_services.get_user_studying_decks_ids(user=user) if is_owner else []
    )

    context = {
        "user": user,
        "user_decks": user_decks,
        "studying_decks_ids": studying_decks_ids,
        "query": query,
        "sort_by": sort_by,
        "is_owner": is_owner,
    }

    return render(request, "users/user_decks.html", context)


@login_required
def user_projects(request, user_id):
    user = user_services.get_user_by_id(user_id=user_id)
    query = request.GET.get("query", "")
    sort_by = request.GET.get("sort_by", "")
    page_number = request.GET.get("page", 1)

    user_projects = project_services.filter_sort_paginate_projects(
        projects=project_services.get_all_user_created_projects(user=user),
        query=query,
        sort_by=sort_by,
        page_number=page_number,
        per_page=10,
    )

    is_owner = user == request.user

    context = {
        "user": user,
        "user_projects": user_projects,
        "query": query,
        "sort_by": sort_by,
        "is_owner": is_owner,
    }

    return render(request, "users/user_projects.html", context)


@login_required
def user_update(request, user_id):
    user = user_services.get_user_by_id(user_id=user_id)

    if user != request.user:
        return redirect(user.get_absolute_url())

    if request.method == "POST":
        if "update_user" in request.POST:
            user_form = UserForm(request.POST, request.FILES, instance=user)
            password_form = UserPasswordChangeForm(user)

            old_email = user.email
            old_codewars_username = user.codewars_username

            if user_form.is_valid():
                cleaned_data = user_form.cleaned_data
                email = cleaned_data.get("email")
                codewars_username = cleaned_data.get("codewars_username")

                user_services.update_user_email(
                    base_url=request.build_absolute_uri("/"),
                    old_email=old_email,
                    new_email=email,
                    user=user,
                )

                create_or_update_user_codewars_profile_task.delay(
                    user_id=user.id,
                    codewars_username=codewars_username,
                    old_codewars_username=old_codewars_username,
                )

                user_form.save()

                messages.success(request, "Данные профиля сохранены!")

                return redirect("user_update", user_id=user.pk)
        elif "change_password" in request.POST:
            user_form = UserForm(instance=user)
            password_form = UserPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                messages.success(request, "Пароль успешно изменен!")

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
    is_email_confirmed, user = user_services.confirm_user_email(
        uidb64=uidb64, token=token
    )

    if is_email_confirmed and user == request.user:
        messages.success(request, "Ваш email успешно подтвержден")
    return redirect("user_update", user_id=request.user.pk)
