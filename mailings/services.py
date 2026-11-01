from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Attempt, Mailing


def stats_key(user_id):
    return f"stats:{user_id}"


class MailingError(Exception):
    """Рассылку нельзя отправить"""


def send_mailing(mailing: Mailing) -> dict:
    if mailing.is_disabled:
        raise MailingError("Рассылка отключена менеджером.")

    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        raise MailingError("Сейчас вне периода рассылки: отправка запрещена.")

    recipients = list(mailing.recipients.all())
    if not recipients:
        raise MailingError("У рассылки нет получателей.")

    ok = fail = 0
    for r in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[r.email],
                fail_silently=False,
            )
            Attempt.objects.create(
                mailing=mailing,
                status=Attempt.SUCCESS,
                server_response=f"Отправлено: {r.email}",
            )
            ok += 1
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                status=Attempt.FAIL,
                server_response=f"{r.email}: {e}",
            )
            fail += 1

    mailing.update_status()
    return {"ok": ok, "fail": fail}
