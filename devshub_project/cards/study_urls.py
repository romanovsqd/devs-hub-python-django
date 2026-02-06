from django.urls import path

from . import views

app_name = 'study'

urlpatterns = [
    path('review/', views.review, name='review'),
    path('review/next-card/', views.next_card, name='next_card'),
    path(
        'review/<int:cardset_id>/<int:card_id>/submit/',
        views.submit, name='submit'
    ),
]
