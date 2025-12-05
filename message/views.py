from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.contrib import messages
from zoneinfo import ZoneInfo

from .models import Conversation, Message, Participant, can_users_message
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

    # Get conversations for this user
    # Get 3 most recent team chats
    team_conversations = Conversation.objects.filter(
        participants=user,
        is_team=True
    ).prefetch_related('participants', 'messages').order_by('-updated_at')[:3]

    # Get all 1-on-1 conversations
    personal_conversations = Conversation.objects.filter(
        participants=user,
        is_team=False,
        is_personal_notes=False
    ).prefetch_related('participants', 'messages').order_by('-updated_at')

    # Combine them - team chats first, then personal
    all_conversations = list(team_conversations) + list(personal_conversations)

    # Prepare conversation data with last message and other participant info
    conversation_data = []
    for conv in all_conversations:
        last_message = conv.get_last_message()
        other_participant = conv.get_other_participant(user)

        conversation_data.append({
            'id': conv.id,
            'is_team': conv.is_team,
            'title': conv.title,
            'other_participant': other_participant,
            'last_message': last_message,
            'last_message_time': conv.get_last_message_time(user),
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

    # Get conversations for sidebar
    # Get 3 most recent team chats
    team_conversations = Conversation.objects.filter(
        participants=user,
        is_team=True
    ).prefetch_related('participants').order_by('-updated_at')[:3]

    # Get all 1-on-1 conversations
    personal_conversations = Conversation.objects.filter(
        participants=user,
        is_team=False,
        is_personal_notes=False
    ).prefetch_related('participants').order_by('-updated_at')

    # Combine them - team chats first, then personal
    all_conversations = list(team_conversations) + list(personal_conversations)

    conversation_data = []
    for conv in all_conversations:
        other_participant = conv.get_other_participant(user)
        conversation_data.append({
            'id': conv.id,
            'is_team': conv.is_team,
            'title': conv.title,
            'other_participant': other_participant,
            'last_message': conv.get_last_message(),
            'last_message_time': conv.get_last_message_time(user),
            'unread_count': conv.get_unread_count(user),
        })

    # Get participant information for team chats
    participants_with_roles = []
    if conversation.is_team:
        from teams.models import TeamMembership

        participants = Participant.objects.filter(
            conversation=conversation
        ).select_related('user', 'user__profile').order_by('role', 'user__username')

        for participant in participants:
            # Get team role
            team_role = 'Member'
            if conversation.team:
                try:
                    membership = TeamMembership.objects.get(
                        team=conversation.team,
                        user=participant.user
                    )
                    team_role = membership.role or 'Member'
                except TeamMembership.DoesNotExist:
                    team_role = 'Former Member'

            participants_with_roles.append({
                'user': participant.user,
                'role': participant.role,
                'team_role': team_role,
                'is_admin': participant.role == 'admin',
            })

    context = {
        'conversation': conversation,
        'conversation_messages': conversation_messages,
        'conversations': conversation_data,
        'current_user': user,
        'other_participant': conversation.get_other_participant(user),
        'is_admin': conversation.is_user_admin(user),
        'participants': participants_with_roles,
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
        reply_to_id = request.POST.get('reply_to', None)
        attachment = request.FILES.get('attachment', None)

        # Message must have either content or attachment
        if not content and not attachment:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        # Validate attachment if present
        if attachment:
            # Check file size (max 10MB)
            if attachment.size > 10 * 1024 * 1024:
                return JsonResponse({'error': 'File size must be less than 10MB'}, status=400)

            # Check file type
            file_ext = attachment.name.split('.')[-1].lower()
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'pdf']
            if file_ext not in allowed_extensions:
                return JsonResponse({'error': 'Only images (JPG, PNG, GIF, WebP, SVG) and PDFs are allowed'}, status=400)

        # Get the message being replied to (if any)
        reply_to_message = None
        if reply_to_id:
            try:
                reply_to_message = Message.objects.get(id=reply_to_id, conversation=conversation)
            except Message.DoesNotExist:
                pass  # Ignore invalid reply_to

        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content,
            reply_to=reply_to_message,
            attachment=attachment
        )

        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()

        # Return JSON response for AJAX
        try:
            avatar_url = user.profile.profile_picture.url if user.profile.profile_picture else None
        except:
            avatar_url = None

        # Convert timestamp to user's timezone
        try:
            user_tz = user.profile.timezone or 'UTC'
            tz = ZoneInfo(user_tz)
            local_time = message.timestamp.astimezone(tz)
            formatted_time = local_time.strftime('%I:%M %p')
        except:
            formatted_time = message.timestamp.strftime('%I:%M %p')

        # Prepare reply_to data
        reply_to_data = None
        if message.reply_to:
            reply_to_data = {
                'id': message.reply_to.id,
                'content': message.reply_to.content[:100],  # Truncate long messages
                'sender': {
                    'username': message.reply_to.sender.username if message.reply_to.sender else 'Unknown',
                    'full_name': message.reply_to.sender.get_full_name() if message.reply_to.sender else 'Unknown',
                }
            }

        # Prepare attachment data
        attachment_data = None
        if message.attachment:
            attachment_data = {
                'url': message.attachment.url,
                'type': message.attachment_type,
                'name': message.attachment.name.split('/')[-1],  # Get filename only
            }

        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': formatted_time,
                'sender': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.get_full_name() or user.username,
                    'avatar': avatar_url,
                },
                'reply_to': reply_to_data,
                'attachment': attachment_data
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

    # Get user's timezone
    try:
        user_tz = user.profile.timezone or 'UTC'
        tz = ZoneInfo(user_tz)
    except:
        user_tz = 'UTC'
        tz = ZoneInfo('UTC')

    # Prepare response
    messages_data = []
    for msg in new_messages:
        # Convert timestamp to user's timezone
        try:
            local_time = msg.timestamp.astimezone(tz)
            formatted_time = local_time.strftime('%I:%M %p')
        except:
            formatted_time = msg.timestamp.strftime('%I:%M %p')

        # Build message data
        message_data = {
            'id': msg.id,
            'content': msg.content,
            'timestamp': formatted_time,
            'message_type': msg.message_type,
        }

        # Add sender info only for regular messages
        if msg.message_type == 'regular' and msg.sender:
            try:
                avatar_url = msg.sender.profile.profile_picture.url if msg.sender.profile.profile_picture else None
            except:
                avatar_url = None

            message_data['sender'] = {
                'id': msg.sender.id,
                'username': msg.sender.username,
                'full_name': msg.sender.get_full_name() or msg.sender.username,
                'avatar': avatar_url,
            }

        # Add reply_to info if message is a reply
        if msg.reply_to:
            message_data['reply_to'] = {
                'id': msg.reply_to.id,
                'content': msg.reply_to.content[:100],
                'sender': {
                    'username': msg.reply_to.sender.username if msg.reply_to.sender else 'Unknown',
                    'full_name': msg.reply_to.sender.get_full_name() if msg.reply_to.sender else 'Unknown',
                }
            }

        # Add attachment info if message has attachment
        if msg.attachment:
            message_data['attachment'] = {
                'url': msg.attachment.url,
                'type': msg.attachment_type,
                'name': msg.attachment.name.split('/')[-1],
            }

        messages_data.append(message_data)

    return JsonResponse({'messages': messages_data})

@login_required
def personal_notes(request, username):
    """Get or create personal notes conversation"""
    user = request.user

    # Verify username matches
    if user.username != username:
        messages.error(request, "Invalid request.")
        return redirect('message:conversations_list', username=user.username)

    # Get or create personal notes conversation
    conversation = Conversation.objects.filter(
        participants=user,
        is_personal_notes=True
    ).first()

    if not conversation:
        # Create new personal notes conversation
        conversation = Conversation.objects.create(
            is_personal_notes=True,
            title="Personal Notes"
        )
        Participant.objects.create(user=user, conversation=conversation)

    # Redirect to the conversation thread
    return redirect('message:conversation_thread', username=username, conversation_id=conversation.id)

@login_required
def create_team_conversation(request, username):
    """Create a new team conversation"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    if request.method == 'POST':
        team_id = request.POST.get('team_id')

        if not team_id:
            return JsonResponse({'error': 'Team ID is required'}, status=400)

        from teams.models import Team, TeamMembership

        # Get the team and verify user is a member
        try:
            team = Team.objects.get(id=team_id, members=user)
        except Team.DoesNotExist:
            return JsonResponse({'error': 'Team not found or you are not a member'}, status=404)

        # Check if team conversation already exists
        existing_conv = Conversation.objects.filter(
            team=team,
            is_team=True
        ).first()

        if existing_conv:
            return JsonResponse({
                'success': True,
                'conversation_id': existing_conv.id,
                'message': 'Team conversation already exists'
            })

        # Create new team conversation
        conversation = Conversation.objects.create(
            is_team=True,
            title=f"{team.name} Team Chat",
            team=team
        )

        # Add all team members as participants with appropriate roles
        team_memberships = TeamMembership.objects.filter(team=team).select_related('user')
        for membership in team_memberships:
            # Team owners and admins get admin role in the chat
            is_admin = membership.role in ['Owner', 'Admin']
            participant_role = 'admin' if is_admin else 'member'

            Participant.objects.create(
                user=membership.user,
                conversation=conversation,
                role=participant_role
            )

        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'message': 'Team conversation created successfully'
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def remove_participant(request, username, conversation_id, user_id):
    """Remove a participant from a team conversation (admin only)"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Check if conversation is a team conversation
    if not conversation.is_team:
        return JsonResponse({'error': 'Can only remove participants from team conversations'}, status=400)

    # Check if user is an admin
    if not conversation.is_user_admin(user):
        return JsonResponse({'error': 'Only admins can remove participants'}, status=403)

    # Get the participant to remove
    try:
        participant_to_remove = Participant.objects.get(
            conversation=conversation,
            user_id=user_id
        )
    except Participant.DoesNotExist:
        return JsonResponse({'error': 'Participant not found'}, status=404)

    # Prevent removing the last admin
    admin_count = Participant.objects.filter(
        conversation=conversation,
        role='admin'
    ).count()

    if participant_to_remove.role == 'admin' and admin_count <= 1:
        return JsonResponse({'error': 'Cannot remove the last admin'}, status=400)

    # Remove the participant
    removed_username = participant_to_remove.user.username
    participant_to_remove.delete()

    return JsonResponse({
        'success': True,
        'message': f'{removed_username} removed from conversation'
    })

@login_required
def rename_conversation(request, username, conversation_id):
    """Rename a team conversation (admin only)"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Check if conversation is a team conversation
    if not conversation.is_team:
        return JsonResponse({'error': 'Can only rename team conversations'}, status=400)

    # Check if user is an admin
    if not conversation.is_user_admin(user):
        return JsonResponse({'error': 'Only admins can rename conversations'}, status=403)

    # Get the new title
    new_title = request.POST.get('title', '').strip()

    if not new_title:
        return JsonResponse({'error': 'Title cannot be empty'}, status=400)

    if len(new_title) > 255:
        return JsonResponse({'error': 'Title is too long (max 255 characters)'}, status=400)

    # Store old title for system message
    old_title = conversation.title

    # Update the conversation title
    conversation.title = new_title
    conversation.save()

    # Create system message announcing the rename
    Message.objects.create(
        conversation=conversation,
        content=f"{user.get_full_name() or user.username} renamed the chat from \"{old_title}\" to \"{new_title}\"",
        message_type='system',
        sender=None
    )

    return JsonResponse({
        'success': True,
        'message': 'Conversation renamed successfully',
        'new_title': new_title
    })

@login_required
def get_thread_messages(request, username, conversation_id, message_id):
    """Get all messages in a thread"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Get the root message
    root_message = get_object_or_404(Message, id=message_id, conversation=conversation)

    # Get all thread replies
    thread_messages = Message.objects.filter(thread_root=root_message).select_related('sender', 'sender__profile').order_by('timestamp')

    # Get user timezone
    try:
        user_tz = user.profile.timezone or 'UTC'
        tz = ZoneInfo(user_tz)
    except:
        user_tz = 'UTC'
        tz = ZoneInfo('UTC')

    # Prepare response data
    messages_data = []
    for msg in thread_messages:
        # Convert timestamp to user's timezone
        try:
            local_time = msg.timestamp.astimezone(tz)
            formatted_time = local_time.strftime('%I:%M %p')
        except:
            formatted_time = msg.timestamp.strftime('%I:%M %p')

        # Get avatar URL
        try:
            avatar_url = msg.sender.profile.profile_picture.url if msg.sender.profile.profile_picture else None
        except:
            avatar_url = None

        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'timestamp': formatted_time,
            'sender': {
                'id': msg.sender.id,
                'username': msg.sender.username,
                'full_name': msg.sender.get_full_name() or msg.sender.username,
                'avatar': avatar_url,
            }
        })

    # Also get root message data
    try:
        root_avatar_url = root_message.sender.profile.profile_picture.url if root_message.sender.profile.profile_picture else None
    except:
        root_avatar_url = None

    try:
        root_local_time = root_message.timestamp.astimezone(tz)
        root_formatted_time = root_local_time.strftime('%I:%M %p')
    except:
        root_formatted_time = root_message.timestamp.strftime('%I:%M %p')

    root_message_data = {
        'id': root_message.id,
        'content': root_message.content,
        'timestamp': root_formatted_time,
        'sender': {
            'id': root_message.sender.id,
            'username': root_message.sender.username,
            'full_name': root_message.sender.get_full_name() or root_message.sender.username,
            'avatar': root_avatar_url,
        }
    }

    return JsonResponse({
        'root_message': root_message_data,
        'messages': messages_data
    })

@login_required
def send_thread_reply(request, username, conversation_id, message_id):
    """Send a reply to a thread"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Get the root message
    root_message = get_object_or_404(Message, id=message_id, conversation=conversation)

    # Get message content
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    # Create the thread reply
    thread_reply = Message.objects.create(
        conversation=conversation,
        sender=user,
        content=content,
        thread_root=root_message
    )

    # Update conversation timestamp
    conversation.updated_at = timezone.now()
    conversation.save()

    # Prepare response
    try:
        avatar_url = user.profile.profile_picture.url if user.profile.profile_picture else None
    except:
        avatar_url = None

    try:
        user_tz = user.profile.timezone or 'UTC'
        tz = ZoneInfo(user_tz)
        local_time = thread_reply.timestamp.astimezone(tz)
        formatted_time = local_time.strftime('%I:%M %p')
    except:
        formatted_time = thread_reply.timestamp.strftime('%I:%M %p')

    return JsonResponse({
        'success': True,
        'message': {
            'id': thread_reply.id,
            'content': thread_reply.content,
            'timestamp': formatted_time,
            'sender': {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name() or user.username,
                'avatar': avatar_url,
            }
        },
        'thread_count': root_message.get_thread_count()
    })

@login_required
def messages_view(request, username):
    """Main messages UI view - Sample UI only"""
    return render(request, 'message/messages.html')

@login_required
def delete_message(request, username, conversation_id, message_id):
    """Delete a message (only the sender can delete their own messages)"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Get the message
    message = get_object_or_404(Message, id=message_id, conversation=conversation)

    # Verify the user is the sender
    if message.sender != user:
        return JsonResponse({'error': 'You can only delete your own messages'}, status=403)

    # Don't allow deleting system messages
    if message.message_type == 'system':
        return JsonResponse({'error': 'Cannot delete system messages'}, status=400)

    # Delete the message
    message.delete()

    return JsonResponse({
        'success': True,
        'message': 'Message deleted successfully'
    })

@login_required
def edit_message(request, username, conversation_id, message_id):
    """Edit a message (only the sender can edit their own messages)"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Get the conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)

    # Get the message
    message = get_object_or_404(Message, id=message_id, conversation=conversation)

    # Verify the user is the sender
    if message.sender != user:
        return JsonResponse({'error': 'You can only edit your own messages'}, status=403)

    # Don't allow editing system messages
    if message.message_type == 'system':
        return JsonResponse({'error': 'Cannot edit system messages'}, status=400)

    # Get the new content
    new_content = request.POST.get('content', '').strip()

    if not new_content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    # Update the message content
    message.content = new_content
    message.save()

    return JsonResponse({
        'success': True,
        'message': 'Message edited successfully',
        'new_content': new_content
    })

@login_required
def poll_sidebar_conversations(request, username):
    """Get recent conversations for sidebar live updates (AJAX polling)"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'error': 'Invalid request'}, status=403)

    # Get user's 3 most recent conversations (excluding personal notes)
    # Prefetch related data to avoid N+1 queries
    conversations = Conversation.objects.filter(
        participants=user,
        is_personal_notes=False
    ).select_related('team').prefetch_related('participants', 'messages').order_by('-updated_at')[:3]

    # Ensure user profile is loaded for timezone
    try:
        user_profile = user.profile
        user_timezone = user_profile.timezone or 'UTC'
    except:
        user_timezone = 'UTC'

    # Prepare conversation data
    conversation_data = []
    for conv in conversations:
        last_message = conv.get_last_message()

        # Determine display name and avatar
        if conv.is_team:
            name = conv.title or f"Team Chat {conv.id}"
            avatar_url = None  # Could add team avatar later
        else:
            other_user = conv.get_other_participant(user)
            if other_user:
                name = other_user.get_full_name() or other_user.username
                # Use UI Avatars
                avatar_url = f"https://ui-avatars.com/api/?name={name}&background=random"
            else:
                continue  # Skip if no other participant

        conversation_data.append({
            'id': conv.id,
            'name': name,
            'avatar_url': avatar_url,
            'last_message_preview': last_message.content[:50] if last_message else 'No messages yet',
            'last_message_time': conv.get_last_message_time(user),
            'has_unread': conv.has_unread_messages(user),
            'unread_count': conv.get_unread_count(user),
        })

    return JsonResponse({'conversations': conversation_data})

@login_required
def delete_conversation(request, username, conversation_id):
    """Delete a team conversation (only team conversations can be deleted)"""
    user = request.user

    # Verify username matches
    if user.username != username:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

    try:
        # Get the conversation
        conversation = Conversation.objects.get(id=conversation_id, participants=user)

        # Only allow deletion of team conversations
        if not conversation.is_team:
            return JsonResponse({'success': False, 'error': 'Only team conversations can be deleted'}, status=400)

        # Check if user is the team admin or conversation creator
        # For now, allow any participant to delete (you can add more restrictions)
        conversation_title = conversation.title or f"Team Chat {conversation.id}"

        # Delete the conversation
        conversation.delete()

        return JsonResponse({
            'success': True,
            'message': f'Conversation "{conversation_title}" deleted successfully'
        })

    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
