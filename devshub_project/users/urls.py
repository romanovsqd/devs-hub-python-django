from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path("<str:username>/", views.user_detail, name="user_detail"),
    path("<str:username>/cards/", views.user_cards, name="user_cards"),
    path("<str:username>/decks/", views.user_decks, name="user_decks"),
    path("<str:username>/projects/", views.user_projects, name="user_projects"),
    path("<str:username>/edit/", views.user_update, name="user_update"),
]
