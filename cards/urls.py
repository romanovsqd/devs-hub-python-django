from django.urls import path

from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.card_list, name='card_list'),
    path('<int:card_id>/', views.card_detail, name='card_detail'),
    path('create/', views.card_create, name='card_create'),
    path('<int:card_id>/edit/', views.card_update, name='card_update'),
]
