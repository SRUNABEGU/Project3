from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("users:activate", kwargs={"uidb64": uid, "token": token})
    link = request.build_absolute_uri(path)
    send_mail(
        subject="Подтверждение регистрации",
        message=(
            "Здравствуйте!\n\n"
            "Для подтверждения email перейдите по ссылке:\n"
            f"{link}\n\n"
            "Если вы не регистрировались, просто проигнорируйте письмо."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
