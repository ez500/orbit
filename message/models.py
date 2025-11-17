from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import uuid

# Create your models here.
   
class Conversation(models.Model):
   id = models.AutoField(primary_key=True)
   is_team = models.BooleanField(default=False)
   title = models.CharField(max_length=255, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   participants = models.ManyToManyField(User, through='Participant')

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
   
class Participant(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
   joined_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
   id = models.AutoField(primary_key=True)
   conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
   sender = models.ForeignKey(User, on_delete=models.CASCADE)
   content = models.TextField()
   timestamp = models.DateTimeField(auto_now_add=True)
   is_read = models.BooleanField(default=False)