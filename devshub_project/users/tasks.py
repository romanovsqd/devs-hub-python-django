from celery import shared_task
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@shared_task
def send_confirmation_email_task(base_url, user_id):
    """
    Генерирует ссылку с токеном и отправляет письмо для подтверждение почты.
    """
    user = get_object_or_404(pk=user_id)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    confirm_url = reverse("confirm_email", kwargs={"uidb64": uid, "token": token})
    confirm_link = f"{base_url[:-1]}{confirm_url}"

    send_mail(
        "Подтверждение почты",
        f"Перейдите по ссылке:\n{confirm_link}",
        "devs-hub@mail.com",
        [user.email],
    )
