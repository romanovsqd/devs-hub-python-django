from datetime import timedelta

import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import CodewarsProfile

User = get_user_model()


@shared_task
def send_confirmation_email_task(base_url, user_id, new_email):
    """
    Генерирует ссылку с токеном и отправляет письмо для подтверждение почты.
    """
    user = get_object_or_404(User, pk=user_id)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    confirm_url = reverse("confirm_email", kwargs={"uidb64": uid, "token": token})
    confirm_link = f"{base_url[:-1]}{confirm_url}"

    send_mail(
        subject="Подтверждение почты",
        message=f"Для подтверждения почты перейдите по ссылке:\n{confirm_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_email],
        fail_silently=False,
    )


@shared_task
def send_reset_email_task(subject, message, email):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def create_or_update_user_codewars_profile_task(
    user_id, codewars_username, old_codewars_username=None
):
    user = User.objects.get(id=user_id)

    if not codewars_username:
        CodewarsProfile.objects.filter(user=user).delete()
        return

    if old_codewars_username == codewars_username:
        return

    url = f"https://www.codewars.com/api/v1/users/{codewars_username}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            CodewarsProfile.objects.filter(user=user).delete()
            return
        data = response.json()
    except requests.RequestException:
        return

    honor = data.get("honor", {})
    leaderboard_position = data.get("leaderboardPosition")
    ranks = data.get("ranks", {})
    languages = list(ranks.get("languages").keys())
    code_challenges = data.get("codeChallenges", {})
    total_completed_katas = code_challenges.get("totalCompleted", 0)

    codewars_data = {
        "honor": honor,
        "leaderboard_position": leaderboard_position,
        "languages": languages,
        "total_completed_katas": total_completed_katas,
    }

    CodewarsProfile.objects.update_or_create(user=user, defaults=codewars_data)


@shared_task
def update_codewars_profiles_task():
    threshold = timezone.now() - timedelta(hours=24)

    profiles = CodewarsProfile.objects.filter(
        updated_at__lt=threshold,
    ).select_related("user")

    for profile in profiles:
        create_or_update_user_codewars_profile_task.delay(
            user_id=profile.user_id,
            codewars_username=profile.user.codewars_username,
        )
