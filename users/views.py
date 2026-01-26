from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from cards.models import Card, CardSet, CardSetProgress

from .forms import LoginForm, RegisterForm, UserForm


User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()

    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


class LoginUserView(LoginView):
    authentication_form = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)


@login_required
def user_list(request):
    query = request.GET.get('query', '')

    if query:
        users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.all()

    context = {
        'users': users,
    }
    return render(request, 'users/users/user_list.html', context)


@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        return redirect('users:profile_detail')

    context = {
        'user': user,
    }
    return render(request, 'users/users/user_detail.html', context)


@login_required
def user_cards(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_cards = Card.objects.filter(
        Q(author=user) | Q(saved_by=user)
    ).distinct()

    context = {
        'user': user,
        'user_cards': user_cards,
    }
    return render(request, 'users/users/user_cards.html', context)


@login_required
def user_cardsets(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_cardsets = CardSet.objects.filter(
        Q(author=user) | Q(saved_by=user)
    ).distinct()

    context = {
        'user': user,
        'user_cardsets': user_cardsets,
    }
    return render(request, 'users/users/user_cardsets.html', context)


@login_required
def user_projects(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_projects = user.projects.all()

    context = {
        'user': user,
        'user_projects': user_projects,
    }
    return render(request, 'users/users/user_projects.html', context)


def profile_detail(request):
    user = request.user

    context = {
        'user': user,
    }
    return render(request, 'users/profile/profile_detail.html', context)


def profile_update(request):
    user = request.user

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserForm(request.POST, request.FILES, instance=user)
            password_form = PasswordChangeForm(user)

            if user_form.is_valid():
                user_form.save()
                return redirect('users:profile_update')

        elif 'change_password' in request.POST:
            user_form = UserForm(instance=user)
            password_form = PasswordChangeForm(user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('users:profile_update')
    else:
        user_form = UserForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'users/profile/profile_form.html', {
        'user_form': user_form,
        'password_form': password_form,
    })



def profile_cards(request):
    user = request.user
    user_cards = Card.objects.filter(
        Q(author=user) | Q(saved_by=user)
    ).distinct()

    context = {
        'user': user,
        'user_cards': user_cards,
    }
    return render(request, 'users/profile/profile_cards.html', context)


def profile_cardsets(request):
    user = request.user
    user_cardsets = CardSet.objects.filter(
        Q(author=user) | Q(saved_by=user)
    ).distinct()

    studying_cardsets_ids = CardSetProgress.objects.filter(
        learner=user,
    ).values_list('cardset_id', flat=True)

    context = {
        'user': user,
        'user_cardsets': user_cardsets,
        'studying_cardsets_ids': studying_cardsets_ids,
    }
    return render(request, 'users/profile/profile_cardsets.html', context)


def profile_projects(request):
    user = request.user
    user_projects = user.projects.all()

    context = {
        'user': user,
        'user_projects': user_projects,
    }
    return render(request, 'users/profile/profile_projects.html', context)
