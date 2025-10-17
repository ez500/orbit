from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name='register'),
    path("login/", views.UserLoginView.as_view(), name='login'),
    path("logout/", views.UserLogoutView.as_view(), name='logout'),
    path("password-reset/", views.UserPasswordResetView.as_view(), name='password_reset'),
    path("password-reset/<uidb64>/<token>/", views.UserPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path("password-reset/done", views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path("edit/", views.edit_user_profile, name='profile_edit'),
    path("settings/", views.settings, name="user_settings"),
    path("<str:username>/", views.ProfileView.as_view(), name='profile_view'),
]
