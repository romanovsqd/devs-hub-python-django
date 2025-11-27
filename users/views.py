from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegisterForm


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
    return render(request, 'users/user_list.html', context)


@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    context = {
        'user': user,
    }
    return render(request, 'users/user_detail.html', context)


@login_required
def user_cards(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    cards = user.cards.all()

    context = {
        'user': user,
        'cards': cards,
    }
    return render(request, 'users/user_cards.html', context)


@login_required
def user_cardsets(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    cardsets = user.cardsets.all()

    context = {
        'user': user,
        'cardsets': cardsets,
    }
    return render(request, 'users/user_cardsets.html', context)


@login_required
def user_projects(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    projects = user.projects.all()

    context = {
        'user': user,
        'projects': projects,
    }
    return render(request, 'users/user_projects.html', context)
