from django.urls import path

from . import views

urlpatterns = [
    path("", views.deck_list, name="deck_list"),
    path("<int:pk>/", views.deck_detail, name="deck_detail"),
    path("create/", views.deck_create, name="deck_create"),
    path("<int:pk>/edit/", views.deck_update, name="deck_update"),
    path("<int:pk>/delete/", views.deck_delete, name="deck_delete"),
]
