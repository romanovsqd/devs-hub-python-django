from django.urls import include, path
from . import views

app_name = 'users'

urlpatterns = [
    # TODO: скрыть /register и /login для авторизованных пользователей
    path('register/', views.register, name='register'),
    path('', include('django.contrib.auth.urls')),
]
