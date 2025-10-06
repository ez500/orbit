from django.urls import path

from . import views

app_name = 'crm'

urlpatterns = [
    path("", views.home, name='home'),
    path("register/", views.register, name='register'),
    path("dashboard/", views.dashboard, name='dashboard') 
]
