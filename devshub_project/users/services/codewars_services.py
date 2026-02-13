import requests

from users.models import CodewarsProfile


def get_user_codewars_stats(user):
    """Возвращает статистику codewars профиля."""
    if user.codewars_username:
        return CodewarsProfile.objects.filter(user=user).first()
    return None


def fetch_codewars_data(codewars_username):
    """Получает статистику codewars профиля по codewars API."""
    url = f"https://www.codewars.com/api/v1/users/{codewars_username}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    honor = data.get("honor", {})
    leaderboard_position = data.get("leaderboardPosition")
    ranks = data.get("ranks", {})
    languages = list(ranks.get("languages").keys())
    code_challenges = data.get("codeChallenges", {})
    total_completed_katas = code_challenges.get("totalCompleted", 0)

    return {
        "honor": honor,
        "leaderboard_position": leaderboard_position,
        "languages": languages,
        "total_completed_katas": total_completed_katas,
    }


def create_or_update_user_codears_profile(
    old_codewars_username, codewars_username, user
):
    """Создает или обновляет данные codewars профиля."""
    if not codewars_username:
        CodewarsProfile.objects.filter(user=user).delete()
        return

    if old_codewars_username == codewars_username:
        return None

    codewars_data = fetch_codewars_data(codewars_username)

    if codewars_data:
        CodewarsProfile.objects.update_or_create(user=user, defaults=codewars_data)
