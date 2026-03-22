from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("auth/register/", views.RegisterView.as_view(), name="api-register"),
]

urlpatterns += router.urls
