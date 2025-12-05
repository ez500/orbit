from django.urls import path
from . import views

app_name = "company"

urlpatterns = [
    path("register/", views.RegisterCompany.as_view(), name="register"),
    path("join/", views.JoinCompanyListView.as_view(), name="join_list"),
    path("<str:name>/announcements/create/", views.CreateAnnouncementView.as_view(), name="create_announcement"),
    path("<str:name>/announcements/<int:pk>/edit/", views.EditAnnouncementView.as_view(), name="edit_announcement"),
    path("<str:name>/edit/", views.EditCompany.as_view(), name="edit"),
    path("<str:name>/send-join-request/", views.send_join_request, name="send_join_request"),
    path("<str:name>/accept/<str:username>", views.accept_join_request, name="accept_join_request"),
    path("<str:name>/decline/<str:username>", views.decline_join_request, name="decline_join_request"),
    path("<str:name>/leave/", views.leave_company, name="leave"),
    path("<str:name>/promote/<str:username>/", views.promote_member, name="promote"),
    path("<str:name>/demote/<str:username>/", views.demote_member, name="demote"),
    path("<str:name>/kick/<str:username>/", views.kick_member, name="kick"),
    path("<str:name>/", views.CompanyView.as_view(), name="company"),

]
