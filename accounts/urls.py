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
    path("search/", views.search, name="user_search"),
    path("send-connection-request/<str:username>/", views.send_connection_request, name='send_connection_request'),
    path("accept-connection-request/<str:username>/", views.accept_connection_request, name='accept_connection_request'),
    path("ignore-connection-request/<str:username>/", views.ignore_connection_request, name='ignore_connection_request'),
    path("remove-connection/<str:username>/", views.remove_connection, name='remove_connection'),
    path("<str:username>/", views.ProfileView.as_view(), name='profile_view'),
    path("<str:username>/companies", views.CompanyListView.as_view(), name='company_list'),
]
