from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, ListView

from .forms import RegisterForm
from .models import User
from .services import send_activation_email


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/form.html"
    success_url = reverse_lazy("users:register_done")
    extra_context = {"title": "Регистрация", "button": "Зарегистрироваться"}

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        send_activation_email(self.request, user)
        return redirect(self.success_url)


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, "Email подтверждён. Теперь можно войти.")
        return redirect("users:login")

    return render(
        request,
        "users/message.html",
        {
            "title": "Ссылка недействительна",
            "text": "Ссылка устарела или уже использована. Попробуйте зарегистрироваться снова.",
        },
    )


class UserListView(PermissionRequiredMixin, ListView):
    model = User
    permission_required = "users.view_user"
    template_name = "users/user_list.html"
    ordering = ["email"]


class UserToggleBlockView(PermissionRequiredMixin, View):
    permission_required = "users.can_block_user"
    http_method_names = ["post"]

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target.pk == request.user.pk or target.is_superuser:
            messages.error(request, "Этого пользователя заблокировать нельзя.")
        else:
            target.is_blocked = not target.is_blocked
            target.save(update_fields=["is_blocked"])
            messages.success(
                request,
                f"{target.email}: {'заблокирован' if target.is_blocked else 'разблокирован'}.",
            )
        return redirect("users:user_list")
