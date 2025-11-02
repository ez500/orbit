from django.urls import path

from . import views

app_name = 'company'

urlpatterns = [
    path("register", views.RegisterCompany.as_view(), name="register"),
    path("<str:name>/", views.CompanyView.as_view(), name="company"),
    path("<str:name>/edit", views.EditCompany.as_view(), name="edit"),
]
