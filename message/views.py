from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.contrib import messages

from .models import Conversation, Message, can_users_message
from .serializer import ConversationSerializer, MessageSerializer

# Create your views here.

def send_test_email(request):
    subject = "email test"
    message = "this is the content of the test email"
    from_email = "veralignhost@gmail.com"
    recipient_list = ['iclausen7991@gmail.com']

    send_mail(subject, message, from_email, recipient_list)

    return render(request, 'message/email_sent.html')

@login_required
def conversations_list(request, username):
    """List all conversations for the current user"""
    user = request.user

    # Verify the username matches the logged-in user
    if user.username != username:
        messages.error(request, "You can only view your own messages.")
        return redirect('message:conversations_list', username=user.username)

    # Get all conversations for this user
    conversations = Conversation.objects.filter(
        participants=user
    ).prefetch_related('participants', 'messages').order_by('-updated_at')

    # Prepare conversation data with last message and other participant info
    conversation_data = []
    for conv in conversations:
        last_message = conv.get_last_message()
        other_participant = conv.get_other_participant(user)

        conversation_data.append({
            'id': conv.id,
            'is_team': conv.is_team,
            'title': conv.title,
            'other_participant': other_participant,
            'last_message': last_message,
            'last_message_time': conv.get_last_message_time(),
            'unread_count': conv.get_unread_count(user),
            'updated_at': conv.updated_at,
        })

    context = {
        'conversations': conversation_data,
        'current_user': user,
    }

    return render(request, 'message/conversations.html', context)

@login_required
def conversation_thread(request, username, conversation_id):
    """View a specific conversation thread"""
    user = request.user

    # Verify the username matches
    if user.username != username:
        messages.error(request, "You can only view your own messages.")
        return redirect('message:conversation_thread', username=user.username, conversation_id=conversation_id)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    # Get all messages in the conversation
    conversation_messages = conversation.messages.select_related('sender').order_by('timestamp')

    # Get all conversations for sidebar
    all_conversations = Conversation.objects.filter(
        participants=user
    ).prefetch_related('participants').order_by('-updated_at')

    conversation_data = []
    for conv in all_conversations:
        other_participant = conv.get_other_participant(user)
        conversation_data.append({
            'id': conv.id,
            'is_team': conv.is_team,
            'title': conv.title,
            'other_participant': other_participant,
            'last_message': conv.get_last_message(),
            'last_message_time': conv.get_last_message_time(),
            'unread_count': conv.get_unread_count(user),
        })

    context = {
        'conversation': conversation,
        'conversation_messages': conversation_messages,
        'conversations': conversation_data,
        'current_user': user,
        'other_participant': conversation.get_other_participant(user),
    }

    return render(request, 'message/thread.html', context)

@login_required
def start_conversation(request, username, other_username):
    """Start or get existing conversation with another user"""
    user = request.user

    # Verify username matches
    if user.username != username:
        messages.error(request, "Invalid request.")
        return redirect('message:conversations_list', username=user.username)

    # Get the other user
    other_user = get_object_or_404(User, username=other_username)

    # Check if users can message each other
    if not can_users_message(user, other_user):
        messages.error(request, f"You can only message your connections or team members.")
        return redirect('accounts:profile', username=other_username)

    # Get or create conversation
    conversation, created = Conversation.get_or_create_conversation(user, other_user)

    if conversation:
        if created:
            messages.success(request, f"Started conversation with {other_user.username}")
        return redirect('message:conversation_thread', username=username, conversation_id=conversation.id)
    else:
        messages.error(request, "Unable to start conversation.")
        return redirect('accounts:profile', username=other_username)

@login_required
def send_message(request, username, conversation_id):
    """Send a message in a conversation"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    if request.method == 'POST':
        # Get the conversation and verify user is a participant
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

        content = request.POST.get('content', '').strip()

        if not content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )

        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()

        # Return JSON response for AJAX
        try:
            avatar_url = user.profile.profile_picture.url if user.profile.profile_picture else None
        except:
            avatar_url = None

        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%I:%M %p'),
                'sender': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name() or user.username,
                    'avatar': avatar_url,
                }
            }
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def search_messageable_users(request, username):
    """Search for users that the current user can message (connections + team members)"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'users': []})

    from accounts.models import Profile
    from teams.models import Team

    # Get user's connections
    try:
        profile = Profile.objects.get(user=user)
        connections = profile.connections.all()
        connection_users = [conn.user for conn in connections]
    except Profile.DoesNotExist:
        connection_users = []

    # Get users in the same teams
    user_teams = Team.objects.filter(members=user)
    team_members = User.objects.filter(teams__in=user_teams).exclude(id=user.id).distinct()

    # Combine and filter by search query
    messageable_users = set(connection_users) | set(team_members)

    # Filter by query (username, first name, last name)
    filtered_users = [
        u for u in messageable_users
        if query.lower() in u.username.lower() or
           query.lower() in u.get_full_name().lower() or
           query.lower() in u.first_name.lower() or
           query.lower() in u.last_name.lower()
    ]

    # Prepare response
    users_data = []
    for u in filtered_users[:10]:  # Limit to 10 results
        try:
            avatar_url = u.profile.profile_picture.url if u.profile.profile_picture else None
        except:
            avatar_url = None

        users_data.append({
            'username': u.username,
            'full_name': u.get_full_name() or u.username,
            'avatar': avatar_url,
        })

    return JsonResponse({'users': users_data})

@login_required
def get_new_messages(request, username, conversation_id):
    """Get new messages since last_message_id for real-time updates"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Get last_message_id from query params
    last_message_id = request.GET.get('last_message_id', 0)
    try:
        last_message_id = int(last_message_id)
    except (ValueError, TypeError):
        last_message_id = 0

    # Get new messages since last_message_id
    new_messages = conversation.messages.filter(
        id__gt=last_message_id
    ).exclude(
        sender=user  # Exclude messages sent by current user (already displayed via AJAX)
    ).select_related('sender').order_by('timestamp')

    # Mark new messages as read
    new_messages.filter(is_read=False).update(is_read=True)

    # Prepare response
    messages_data = []
    for msg in new_messages:
        try:
            avatar_url = msg.sender.profile.profile_picture.url if msg.sender.profile.profile_picture else None
        except:
            avatar_url = None

        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
            'sender': {
                'id': msg.sender.id,
                'username': msg.sender.username,
                'full_name': msg.sender.get_full_name() or msg.sender.username,
                'avatar': avatar_url,
            }
        })

    return JsonResponse({'messages': messages_data})

@login_required
def messages_view(request, username):
    """Main messages UI view - Sample UI only"""
    return render(request, 'message/messages.html')
