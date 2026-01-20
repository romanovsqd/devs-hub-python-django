from django.urls import path

from . import views

app_name = 'cardsets'

urlpatterns = [
    path('', views.cardset_list, name='cardset_list'),
    path('<int:cardset_id>/', views.cardset_detail, name='cardset_detail'),
    path('create/', views.cardset_create, name='cardset_create'),
    path(
        '<int:cardset_id>/edit/', views.cardset_update, name='cardset_update'
    ),
    path(
        '<int:cardset_id>/delete/', views.cardset_delete, name='cardset_delete'
    ),
    path(
        '<int:cardset_id>/toggle-save/',
        views.cardset_toggle_save, name='cardset_toggle_save'
    ),
    path(
        '<int:cardset_id>/toggle-study/',
        views.cardset_toggle_study, name='cardset_toggle_study'
    ),
]
