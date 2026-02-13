from users.models import CodewarsProfile


def get_user_codewars_stats(user):
    """Возвращает статистику codewars профиля."""
    if user.codewars_username:
        return CodewarsProfile.objects.filter(user=user).first()
    return None
