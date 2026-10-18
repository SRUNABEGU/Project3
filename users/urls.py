from django.contrib.auth import views as auth
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from . import views

app_name = "users"

MSG = "users/message.html"

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user_list"),
    path(
        "users/<int:pk>/block/", views.UserToggleBlockView.as_view(), name="user_block"
    ),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "register/done/",
        TemplateView.as_view(
            template_name=MSG,
            extra_context={
                "title": "Проверьте почту",
                "text": "Мы отправили письмо со ссылкой для подтверждения.",
            },
        ),
        name="register_done",
    ),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path(
        "login/", auth.LoginView.as_view(template_name="users/login.html"), name="login"
    ),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth.PasswordResetView.as_view(
            template_name="users/form.html",
            extra_context={
                "title": "Восстановление пароля",
                "button": "Отправить ссылку",
            },
            email_template_name="users/password_reset_email.txt",
            subject_template_name="users/password_reset_subject.txt",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth.PasswordResetDoneView.as_view(
            template_name=MSG,
            extra_context={
                "title": "Письмо отправлено",
                "text": "Если такой email зарегистрирован, мы отправили ссылку для сброса пароля.",
            },
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth.PasswordResetCompleteView.as_view(
            template_name=MSG,
            extra_context={
                "title": "Пароль изменён",
                "text": "Теперь можно войти с новым паролем.",
            },
        ),
        name="password_reset_complete",
    ),
]
