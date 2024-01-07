from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


app_name = 'account'
urlpatterns = [
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_change/", views.PassChangeView.as_view(), name="password_change"),
    path("password_reset/", views.PassResetView.as_view(), name="password_reset"),
    path("password_reset_confirm/<uidb64>/<token>", views.PassResetConfirmView.as_view(), name="password_reset_confirm"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/update/<int:pk>/", views.ProfileUpdateView.as_view(), name="profile_update"),
    path("profile/delete/<int:pk>", views.ProfileDeleteView.as_view(), name="profile_delete"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register_confirm/<uidb64>/<token>", views.RegisterConfirmView.as_view(), name="register_confirm"),
    path("email_change/", views.EmailChangeView.as_view(), name="email_change"),
    path("email_change_confirm/<uidb64>/<token>/<email>", views.EmailChangeConfirmView.as_view(), name="email_change_confirm"),
]