from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path("<int:user_id>/", views.user_detail, name="user_detail"),
    path("<int:user_id>/cards/", views.user_cards, name="user_cards"),
    path("<int:user_id>/card-sets/", views.user_decks, name="user_decks"),
    path("<int:user_id>/projects/", views.user_projects, name="user_projects"),
    path("<int:user_id>/edit/", views.user_update, name="user_update"),
]
