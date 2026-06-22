from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-done/', views.PasswordResetDoneView.as_view(), name='password-reset-done'),
    path(
        'password-reset/<uidb64>/<token>/',
        views.PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
]
