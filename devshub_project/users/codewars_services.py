import requests

from .models import CodewarsProfile


def get_user_codewars_stats(user):
    if user.codewars_username:
        return user.codewars_profile
    return None


def fetch_codewars_data(codewars_username):
    url = f'https://www.codewars.com/api/v1/users/{codewars_username}'
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    honor = data.get('honor', {})
    leaderboard_position = data.get('leaderboardPosition')
    ranks = data.get('ranks', {})
    languages = list(ranks.get('languages').keys())
    code_challenges = data.get('codeChallenges', {})
    total_completed_katas = code_challenges.get('totalCompleted', 0)

    return {
        'honor': honor,
        'leaderboard_position': leaderboard_position,
        'languages': languages,
        'total_completed_katas': total_completed_katas,
    }


def create_or_update_user_codears_profile(
    old_codewars_username, codewars_username, user
):
    if not codewars_username:
        return None

    if old_codewars_username == codewars_username:
        return None

    codewars_data = fetch_codewars_data(codewars_username)

    if codewars_data:
        CodewarsProfile.objects.update_or_create(
            user=user,
            defaults=codewars_data
        )
