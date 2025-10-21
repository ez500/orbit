from django.urls import path

from . import views

app_name = 'message'

urlpatterns = [
    path("<str:username>/conversations/", views.conversations, name='conversations'),
    path("send_email/", views.send_test_email, name='send_test_email'),
    
]
