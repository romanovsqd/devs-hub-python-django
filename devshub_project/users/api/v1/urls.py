from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="api-register"),
]

urlpatterns += router.urls
