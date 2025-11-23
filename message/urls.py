from django.urls import path

from . import views

app_name = 'message'

urlpatterns = [
    # Main messages view (sample UI)
    path("<str:username>/", views.messages_view, name='messages'),

    # Conversations list
    path("<str:username>/conversations/", views.conversations_list, name='conversations_list'),

    # View specific conversation thread
    path("<str:username>/conversation/<int:conversation_id>/", views.conversation_thread, name='conversation_thread'),

    # Start a new conversation with a user
    path("<str:username>/start/<str:other_username>/", views.start_conversation, name='start_conversation'),

    # Send a message
    path("<str:username>/conversation/<int:conversation_id>/send/", views.send_message, name='send_message'),

    # Search for messageable users (AJAX)
    path("<str:username>/search-users/", views.search_messageable_users, name='search_users'),

    # Get new messages for polling (AJAX)
    path("<str:username>/conversation/<int:conversation_id>/poll/", views.get_new_messages, name='poll_messages'),

    # Test email (legacy)
    path("send_email/", views.send_test_email, name='send_test_email'),
]
