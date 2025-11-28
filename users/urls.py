from django.urls import include, path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),

    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/cards/', views.user_cards, name='user_cards'),
    path(
        'users/<int:user_id>/card-sets/',
        views.user_cardsets, name='user_cardsets'
    ),
    path(
        'users/<int:user_id>/projects/',
        views.user_projects, name='user_projects',
    ),
]
