from django.urls import path

from . import views

urlpatterns = [
    path("repetitions/review/next_card/", views.NextCard.as_view(), name="next-card"),
    path(
        "repetitions/review/<int:deck_id>/<int:card_id>/submit/",
        views.Submit.as_view(),
        name="submit",
    ),
]
