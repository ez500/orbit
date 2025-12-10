from .models import Conversation

def recent_conversations(request):
    """
    Context processor to provide the three most recent conversations
    for the sidebar across all pages.
    """
    if not request.user.is_authenticated:
        return {'recent_conversations': []}

    # Get user's conversations ordered by most recent activity
    conversations = Conversation.objects.filter(
        participants=request.user,
        is_personal_notes=False  # Exclude personal notes
    ).order_by('-updated_at')[:3]

    # Prepare conversation data with additional context
    conversation_data = []
    for conv in conversations:
        last_message = conv.get_last_message()

        # Determine display name and avatar
        if conv.is_team:
            name = conv.title or f"Team Chat {conv.id}"
            avatar_url = None  # Could add team avatar later
        else:
            other_user = conv.get_other_participant(request.user)
            if other_user:
                name = other_user.get_full_name() or other_user.username
                # Use UI Avatars for now
                avatar_url = f"https://ui-avatars.com/api/?name={name}&background=random"
            else:
                continue  # Skip if no other participant

        conversation_data.append({
            'id': conv.id,
            'name': name,
            'avatar_url': avatar_url,
            'last_message_preview': last_message.content[:50] if last_message else 'No messages yet',
            'last_message_time': conv.get_last_message_time(request.user),
            'has_unread': conv.has_unread_messages(request.user),
            'unread_count': conv.get_unread_count(request.user),
        })

    return {'recent_conversations': conversation_data}
