from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q

from .models import Conversation, Message
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
def messages_view(request, username):
    """Main messages UI view - Sample UI only"""
    return render(request, 'message/messages.html')
