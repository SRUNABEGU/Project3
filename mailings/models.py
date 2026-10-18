from django.conf import settings
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField("Ф. И. О.", max_length=255)
    comment = models.TextField("Комментарий", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipients"
    )

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class Message(models.Model):
    subject = models.CharField("Тема", max_length=255)
    body = models.TextField("Тело письма")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages"
    )

    def __str__(self):
        return self.subject


class Mailing(models.Model):

    class Meta:
        permissions = [("can_disable_mailing", "Может отключать рассылки")]

    CREATED, STARTED, FINISHED = "Создана", "Запущена", "Завершена"
    STATUSES = [(s, s) for s in (CREATED, STARTED, FINISHED)]

    start_time = models.DateTimeField("Начало")
    end_time = models.DateTimeField("Окончание")
    status = models.CharField(max_length=20, choices=STATUSES, default=CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mailings"
    )
    is_disabled = models.BooleanField("Отключена менеджером", default=False)

    def calc_status(self):
        now = timezone.now()
        if now < self.start_time:
            return self.CREATED
        if now <= self.end_time:
            return self.STARTED
        return self.FINISHED

    def update_status(self):
        new = self.calc_status()
        if new != self.status:
            self.status = new
            self.save(update_fields=["status"])

    def __str__(self):
        return f"Рассылка #{self.pk}"


class Attempt(models.Model):
    SUCCESS, FAIL = "Успешно", "Не успешно"
    STATUSES = [(SUCCESS, SUCCESS), (FAIL, FAIL)]

    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUSES)
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, related_name="attempts"
    )
