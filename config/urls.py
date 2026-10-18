from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from mailings.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        cache_page(settings.CACHE_TTL)(vary_on_cookie(HomeView.as_view())),
        name="home",
    ),
    path("", include("users.urls")),
    path("", include("mailings.urls")),
]
