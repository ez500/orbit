from django.urls import path

from . import views

app_name = 'message'

urlpatterns = [
    path("<str:username>/conversations/", views.conversations, name='conversations'),
    path("<str:username>/conversations/start/", views.start_conversation, name="start_conversation"),
    path("<str:username>/conversations/<uuid:conversation_id>/", views.thread, name="thread"),
    
]
