from django.core.management.base import BaseCommand, CommandError

from mailings.models import Mailing
from mailings.services import MailingError, send_mailing


class Command(BaseCommand):
    help = "Отправить рассылку по её id"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **opts):
        try:
            mailing = Mailing.objects.get(pk=opts["mailing_id"])
        except Mailing.DoesNotExist:
            raise CommandError("Рассылка не найдена")
        try:
            result = send_mailing(mailing)
        except MailingError as e:
            raise CommandError(str(e))
        self.stdout.write(
            self.style.SUCCESS(
                f"Отправлено: {result['ok']}, с ошибкой: {result['fail']}"
            )
        )
