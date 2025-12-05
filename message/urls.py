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

    # Poll sidebar conversations for live updates (AJAX)
    path("<str:username>/poll-sidebar/", views.poll_sidebar_conversations, name='poll_sidebar'),

    # Personal notes
    path("<str:username>/notes/", views.personal_notes, name='personal_notes'),

    # Orbit Chat
    path("<str:username>/orbit-chat/", views.orbit_chat, name='orbit_chat'),

    # Create team conversation
    path("<str:username>/create-team-chat/", views.create_team_conversation, name='create_team_conversation'),

    # Remove participant from team conversation (admin only)
    path("<str:username>/conversation/<int:conversation_id>/remove/<int:user_id>/", views.remove_participant, name='remove_participant'),

    # Rename team conversation (admin only)
    path("<str:username>/conversation/<int:conversation_id>/rename/", views.rename_conversation, name='rename_conversation'),

    # Thread functionality
    path("<str:username>/conversation/<int:conversation_id>/thread/<int:message_id>/", views.get_thread_messages, name='get_thread'),
    path("<str:username>/conversation/<int:conversation_id>/thread/<int:message_id>/reply/", views.send_thread_reply, name='send_thread_reply'),

    # Delete and edit messages
    path("<str:username>/conversation/<int:conversation_id>/message/<int:message_id>/delete/", views.delete_message, name='delete_message'),
    path("<str:username>/conversation/<int:conversation_id>/message/<int:message_id>/edit/", views.edit_message, name='edit_message'),

    # Delete conversation
    path("<str:username>/conversation/<int:conversation_id>/delete/", views.delete_conversation, name='delete_conversation'),

    # Test email (legacy)
    path("send_email/", views.send_test_email, name='send_test_email'),
]
