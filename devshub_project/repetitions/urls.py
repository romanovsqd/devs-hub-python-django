from django.urls import path

from . import views

urlpatterns = [
    path(
        "<int:deck_id>/toggle-study/", views.deck_toggle_study, name="deck_toggle_study"
    ),
    path("review/", views.review, name="review"),
    path("review/next-card/", views.next_card, name="next_card"),
    path("review/<int:deck_id>/<int:card_id>/submit/", views.submit, name="submit"),
]
