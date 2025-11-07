from django.urls import path
from . import views

app_name = "company"

urlpatterns = [
    path("register/", views.RegisterCompany.as_view(), name="register"),
    path("join/", views.JoinCompanyListView.as_view(), name="join_list"),

    path("<str:name>/edit/", views.EditCompany.as_view(), name="edit"),
    path("<str:name>/join/", views.join_company, name="join"),
    path("<str:name>/promote/<str:username>/", views.promote_member, name="promote"),
    path("<str:name>/demote/<str:username>/", views.demote_member, name="demote"),
    path("<str:name>/kick/<str:username>/", views.kick_member, name="kick"),
    path("<str:name>/", views.CompanyView.as_view(), name="company"),

]
