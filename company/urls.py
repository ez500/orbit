from django.urls import path

from . import views

app_name = 'company'

urlpatterns = [
    path("<str:name>/", views.CompanyView.as_view(), name="company"),
]
