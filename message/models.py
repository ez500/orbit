from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.db.models import Q
import uuid

# Create your models here.

def can_users_message(user1, user2):
    """
    Check if two users can message each other.
    They can message if they are:
    1. Connected (via Profile.connections)
    2. Members of the same team
    """
    from accounts.models import Profile
    from teams.models import Team

    # Check if they are connections
    try:
        profile1 = Profile.objects.get(user=user1)
        if profile1.connections.filter(user=user2).exists():
            return True
    except Profile.DoesNotExist:
        pass

    # Check if they share a team
    common_teams = Team.objects.filter(members=user1).filter(members=user2)
    if common_teams.exists():
        return True

    return False
   
class Conversation(models.Model):
   id = models.AutoField(primary_key=True)
   is_team = models.BooleanField(default=False)
   title = models.CharField(max_length=255, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   participants = models.ManyToManyField(User, through='Participant')

   @classmethod
   def get_or_create_conversation(cls, user1, user2):
       """
       Get or create a 1-on-1 conversation between two users.
       Only creates if users are allowed to message each other.
       Returns (conversation, created) tuple or (None, False) if not allowed.
       """
       # Check if users can message each other
       if not can_users_message(user1, user2):
           return None, False

       # Look for existing conversation between these two users
       conversations = cls.objects.filter(
           participants=user1,
           is_team=False
       ).filter(participants=user2)

       if conversations.exists():
           return conversations.first(), False

       # Create new conversation
       conversation = cls.objects.create(is_team=False)
       Participant.objects.create(user=user1, conversation=conversation)
       Participant.objects.create(user=user2, conversation=conversation)

       return conversation, True

   def get_other_participant(self, current_user=None):
       """Get the other participant in a 1-on-1 conversation"""
       if self.is_team or not current_user:
           return None
       participants = self.participants.exclude(id=current_user.id)
       return participants.first() if participants.exists() else None

   def get_last_message(self):
       """Get the most recent message in the conversation"""
       return self.messages.order_by('-timestamp').first()

   def get_last_message_time(self):
       """Get formatted time of last message"""
       from django.utils import timezone
       from datetime import timedelta

       last_msg = self.get_last_message()
       if not last_msg:
           return ""

       now = timezone.now()
       diff = now - last_msg.timestamp

       if diff < timedelta(minutes=1):
           return "Just now"
       elif diff < timedelta(hours=1):
           minutes = int(diff.total_seconds() / 60)
           return f"{minutes}m"
       elif diff < timedelta(days=1):
           hours = int(diff.total_seconds() / 3600)
           return f"{hours}h"
       elif diff < timedelta(days=7):
           days = diff.days
           return f"{days}d"
       else:
           return last_msg.timestamp.strftime("%b %d")

   def has_unread_messages(self, user):
       """Check if conversation has unread messages for user"""
       return self.messages.filter(is_read=False).exclude(sender=user).exists()

   def get_unread_count(self, user):
       """Get count of unread messages for user"""
       return self.messages.filter(is_read=False).exclude(sender=user).count()

   def __str__(self):
       if self.is_team:
           return self.title or f"Team Conversation {self.id}"
       participants = list(self.participants.all()[:2])
       if len(participants) == 2:
           return f"{participants[0].username} & {participants[1].username}"
       return f"Conversation {self.id}"

class Participant(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
   joined_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
       return f"{self.user.username} in {self.conversation.id}"

class Message(models.Model):
   id = models.AutoField(primary_key=True)
   conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
   sender = models.ForeignKey(User, on_delete=models.CASCADE)
   content = models.TextField()
   timestamp = models.DateTimeField(auto_now_add=True)
   is_read = models.BooleanField(default=False)

   def __str__(self):
       return f"{self.sender.username}: {self.content[:50]}"