from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("users.auth_urls")),
    path("tinymce/", include("tinymce.urls")),
    path("users/", include("users.urls")),
    path("cards/", include("cards.urls")),
    path("decks/", include("decks.urls")),
    path("repetitions/", include("repetitions.urls")),
    path("projects/", include("projects.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/", include("users.api.v1.urls")),
    path("api/v1/", include("cards.api.v1.urls")),
    path("api/v1/", include("decks.api.v1.urls")),
    path("api/v1/", include("projects.api.v1.urls")),
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
