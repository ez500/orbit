from django.urls import path

from . import views


app_name = 'home'

urlpatterns = [
    path("", views.home, name='home'),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
