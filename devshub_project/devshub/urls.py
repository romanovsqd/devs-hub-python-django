from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.auth_urls")),
    path("", include("core.urls")),
    path("users/", include("users.urls")),
    path("cards/", include("cards.urls")),
    path("decks/", include("decks.urls")),
    path("repetitions/", include("repetitions.urls")),
    path("projects/", include("projects.urls")),
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
