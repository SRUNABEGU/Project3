from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    is_blocked = models.BooleanField("Заблокирован", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        permissions = [("can_block_user", "Может блокировать пользователей")]
