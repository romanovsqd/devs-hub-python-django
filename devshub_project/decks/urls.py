from django.urls import path

from . import views

urlpatterns = [
    path("", views.deck_list, name="deck_list"),
    path("<int:deck_id>/", views.deck_detail, name="deck_detail"),
    path("create/", views.deck_create, name="deck_create"),
    path("<int:deck_id>/edit/", views.deck_update, name="deck_update"),
    path("<int:deck_id>/delete/", views.deck_delete, name="deck_delete"),
    path("<int:deck_id>/toggle-save/", views.deck_toggle_save, name="deck_toggle_save"),
    path("<int:deck_id>/export/", views.deck_export, name="deck_export"),
]
