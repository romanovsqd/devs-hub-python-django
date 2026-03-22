from rest_framework.routers import SimpleRouter

from .views import CardViewSet

router = SimpleRouter()
router.register(r"cards", CardViewSet, basename="card")

urlpatterns = router.urls
