from django import forms
from django.utils import timezone

from .models import Mailing, Message, Recipient

DT_FORMAT = "%Y-%m-%dT%H:%M"


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "message", "recipients"]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format=DT_FORMAT
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format=DT_FORMAT
            ),
            "recipients": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)

    def clean(self):
        data = super().clean()
        start, end = data.get("start_time"), data.get("end_time")
        if start and end:
            if end <= start:
                raise forms.ValidationError("Окончание должно быть позже начала")
            if not self.instance.pk and start < timezone.now():
                raise forms.ValidationError("Начало не может быть в прошлом")
        return data
