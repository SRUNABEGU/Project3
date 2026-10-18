from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Attempt, Mailing, Message, Recipient
from .services import MailingError, send_mailing, stats_key


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx["mailings_total"] = Mailing.objects.count()
        ctx["mailings_active"] = Mailing.objects.filter(
            start_time__lte=now, end_time__gte=now, is_disabled=False
        ).count()
        ctx["recipients_total"] = Recipient.objects.count()
        return ctx


class MailingSendView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
        try:
            result = send_mailing(mailing)
        except MailingError as e:
            messages.error(request, str(e))
        else:
            text = f"Отправлено: {result['ok']}, с ошибкой: {result['fail']}."
            if result["ok"] == 0:
                messages.error(request, text)
            elif result["fail"]:
                messages.warning(request, text)
            else:
                messages.success(request, text)
        return redirect("mailings:mailing_detail", pk=pk)


class OwnerQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class ViewAllQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        qs = super().get_queryset()
        meta = qs.model._meta
        if self.request.user.has_perm(f"{meta.app_label}.view_{meta.model_name}"):
            return qs
        return qs.filter(owner=self.request.user)


class SetOwnerMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class UserFormKwargsMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


FORM_TEMPLATE = "mailings/form.html"
DELETE_TEMPLATE = "mailings/confirm_delete.html"


class RecipientListView(ViewAllQuerysetMixin, ListView):
    model = Recipient


class RecipientDetailView(ViewAllQuerysetMixin, DetailView):
    model = Recipient


class RecipientCreateView(LoginRequiredMixin, SetOwnerMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = FORM_TEMPLATE
    success_url = reverse_lazy("mailings:recipient_list")


class RecipientUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = FORM_TEMPLATE
    success_url = reverse_lazy("mailings:recipient_list")


class RecipientDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Recipient
    template_name = DELETE_TEMPLATE
    success_url = reverse_lazy("mailings:recipient_list")


class MessageListView(OwnerQuerysetMixin, ListView):
    model = Message


class MessageDetailView(OwnerQuerysetMixin, DetailView):
    model = Message


class MessageCreateView(LoginRequiredMixin, SetOwnerMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = FORM_TEMPLATE
    success_url = reverse_lazy("mailings:message_list")


class MessageUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = FORM_TEMPLATE
    success_url = reverse_lazy("mailings:message_list")


class MessageDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Message
    template_name = DELETE_TEMPLATE
    success_url = reverse_lazy("mailings:message_list")


class MailingListView(ViewAllQuerysetMixin, ListView):
    model = Mailing

    def get_queryset(self):
        qs = super().get_queryset().select_related("message", "owner")
        for mailing in qs:
            mailing.update_status()
        return qs


class MailingDetailView(ViewAllQuerysetMixin, DetailView):
    model = Mailing

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(
    LoginRequiredMixin, SetOwnerMixin, UserFormKwargsMixin, CreateView
):
    model = Mailing
    form_class = MailingForm
    template_name = FORM_TEMPLATE
    success_url = reverse_lazy("mailings:mailing_list")


class MailingUpdateView(OwnerQuerysetMixin, UserFormKwargsMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = FORM_TEMPLATE
    success_url = reverse_lazy("mailings:mailing_list")


class MailingDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Mailing
    template_name = DELETE_TEMPLATE
    success_url = reverse_lazy("mailings:mailing_list")


class MailingToggleDisabledView(PermissionRequiredMixin, View):
    permission_required = "mailings.can_disable_mailing"
    http_method_names = ["post"]

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_disabled = not mailing.is_disabled
        mailing.save(update_fields=["is_disabled"])
        messages.success(
            request,
            (
                "Рассылка отключена."
                if mailing.is_disabled
                else "Рассылка снова включена."
            ),
        )
        return redirect("mailings:mailing_detail", pk=pk)


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "mailings/statistics.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        key = stats_key(user.pk)
        totals = cache.get(key)
        if totals is None:
            totals = Attempt.objects.filter(mailing__owner=user).aggregate(
                success=Count("pk", filter=Q(status=Attempt.SUCCESS)),
                fail=Count("pk", filter=Q(status=Attempt.FAIL)),
            )
            cache.set(key, totals, settings.CACHE_TTL)

        success, fail = totals["success"], totals["fail"]
        total = success + fail

        ctx["success"] = success
        ctx["fail"] = fail
        ctx["total"] = total
        ctx["rate"] = round(success / total * 100) if total else 0

        ctx["mailings"] = (
            Mailing.objects.filter(owner=user)
            .select_related("message")
            .annotate(
                success=Count("attempts", filter=Q(attempts__status=Attempt.SUCCESS)),
                fail=Count("attempts", filter=Q(attempts__status=Attempt.FAIL)),
            )
            .order_by("-pk")
        )
        return ctx
