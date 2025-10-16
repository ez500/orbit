from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path("", views.home, name='home'),
    path("dashboard/", views.dashboard, name='dashboard'), 
    path("message/", views.message, name='message')
]
