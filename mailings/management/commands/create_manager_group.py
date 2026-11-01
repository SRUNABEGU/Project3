from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

PERMS = [
    ("mailings", "view_mailing"),
    ("mailings", "view_recipient"),
    ("mailings", "can_disable_mailing"),
    ("users", "view_user"),
    ("users", "can_block_user"),
]


class Command(BaseCommand):
    help = "Создать группу «Менеджеры» с нужными правами"

    def handle(self, *args, **opts):
        group, _ = Group.objects.get_or_create(name="Менеджеры")
        group.permissions.set(
            Permission.objects.get(content_type__app_label=app, codename=code)
            for app, code in PERMS
        )
        self.stdout.write(self.style.SUCCESS("Группа «Менеджеры» готова"))
