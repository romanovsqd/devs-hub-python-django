from django.urls import path

from . import views

urlpatterns = [
    path("", views.card_list, name="card_list"),
    path("<int:pk>/", views.card_detail, name="card_detail"),
    path("create/", views.card_create, name="card_create"),
    path("<int:pk>/edit/", views.card_update, name="card_update"),
    path("<int:pk>/delete/", views.card_delete, name="card_delete"),
    path("<int:pk>/toggle-save/", views.card_toggle_save, name="card_toggle_save"),
    path("<int:pk>/export/", views.card_export, name="card_export"),
]
