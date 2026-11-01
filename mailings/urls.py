from django.urls import path

from . import views as v

app_name = "mailings"

urlpatterns = [
    path("recipients/", v.RecipientListView.as_view(), name="recipient_list"),
    path("recipients/new/", v.RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipients/<int:pk>/", v.RecipientDetailView.as_view(), name="recipient_detail"
    ),
    path(
        "recipients/<int:pk>/edit/",
        v.RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipients/<int:pk>/delete/",
        v.RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path("messages/", v.MessageListView.as_view(), name="message_list"),
    path("messages/new/", v.MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/", v.MessageDetailView.as_view(), name="message_detail"),
    path(
        "messages/<int:pk>/edit/", v.MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "messages/<int:pk>/delete/",
        v.MessageDeleteView.as_view(),
        name="message_delete",
    ),
    path("mailings/", v.MailingListView.as_view(), name="mailing_list"),
    path("mailings/new/", v.MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/<int:pk>/", v.MailingDetailView.as_view(), name="mailing_detail"),
    path(
        "mailings/<int:pk>/edit/", v.MailingUpdateView.as_view(), name="mailing_update"
    ),
    path(
        "mailings/<int:pk>/delete/",
        v.MailingDeleteView.as_view(),
        name="mailing_delete",
    ),
    path("mailings/<int:pk>/send/", v.MailingSendView.as_view(), name="mailing_send"),
    path(
        "mailings/<int:pk>/toggle/",
        v.MailingToggleDisabledView.as_view(),
        name="mailing_toggle",
    ),
    path("statistics/", v.StatisticsView.as_view(), name="statistics"),
]
