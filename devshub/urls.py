from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    path('cards/', include('cards.urls', namespace='cards')),
    path('card-sets/', include('cards.urls_cardsets', namespace='cardsets')),
    path('study/', include('cards.study_urls', namespace='study')),
    path('projects/', include('projects.urls', namespace='projects')),
] + debug_toolbar_urls()

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
