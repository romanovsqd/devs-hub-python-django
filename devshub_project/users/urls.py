from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetDoneView
)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path(
        'password_reset/',
        views.UserPasswordResetView.as_view(), name="password_reset"
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),

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
    path('users/<int:user_id>/edit/', views.user_update, name='user_update'),

    path(
        'confirm-email/<uidb64>/<token>/',
        views.confirm_email, name='confirm_email'
    )
]
