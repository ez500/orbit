from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from .models import Conversation, Message
from .serializer import ConversationSerializer, MessageSerializer

# Create your views here.
@login_required
def conversations(request, username):
    user = request.user
    
    conversations = Conversation.objects.filter(participants=user).order_by('-updated_at')
    
    serializer = ConversationSerializer(conversations, many=True)
    
    context = {
        'conversations' : serializer.data
    }

    return render(request, 'message/conversations.html', context)

@login_required
def thread(request, username, conversation_id):
    user = request.user
    
    conversations = Conversation.objects.filter(participants=user).order_by('-updated_at')
    conversationSerializer = ConversationSerializer(conversations, many=True)
    
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages = conversation.messages
    
    context = {
        'conversations' : conversationSerializer.data,
        'conversation' : conversation,
        'messages' : messages,
    }
    return render(request, 'message/thread.html', context)

@login_required
def start_conversation(request, username):
    # The user we want to message
    other_user = get_object_or_404(User, username=username)
    user = request.user
    
    conversations = Conversation.objects.filter(participants=user).order_by('-updated_at')
    conversationSerializer = ConversationSerializer(conversations, many=True)

    # Step 1: Check if a conversation between these two users already exists
    conversation = (
        Conversation.objects
        .filter(participants=user)
        .filter(participants=other_user)
        .first()
    )

    # Step 2: If it doesn’t exist, create one and add both participants
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(user)
        conversation.participants.add(other_user)
        conversation.save()

    # Step 3: If user sends an initial message
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=user,
                content=content
            )
            return redirect('conversation_detail', conversation_id=conversation.id)

    # Step 4: Show existing messages if any
    messages = conversation.messages.all().order_by('timestamp')
    
    context = {
        'conversations' : conversationSerializer.data,
        'conversation' : conversation,
        'messages' : messages,
    }

    return render(request, 'message/thread.html', context)
