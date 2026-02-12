from functools import wraps
from django.shortcuts import redirect


def redirect_authenticated(view):
    """Редиректит авторизованного пользователя на его профиль."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('user_detail', user_id=request.user.pk)
        return view(request, *args, **kwargs)
    return wrapper
