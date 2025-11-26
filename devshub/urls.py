from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    path('cards/', include('cards.urls', namespace='cards')),
    path('projects/', include('projects.urls', namespace='projects')),
] + debug_toolbar_urls()
