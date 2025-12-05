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
   is_personal_notes = models.BooleanField(default=False)
   title = models.CharField(max_length=255, blank=True)
   team = models.ForeignKey('teams.Team', null=True, blank=True, on_delete=models.CASCADE, related_name='conversations')
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
       if self.is_team or self.is_personal_notes or not current_user:
           return None
       participants = self.participants.exclude(id=current_user.id)
       return participants.first() if participants.exists() else None

   def get_last_message(self):
       """Get the most recent message in the conversation"""
       return self.messages.order_by('-timestamp').first()

   def get_last_message_time(self, user=None):
       """Get formatted time of last message in user's timezone"""
       from django.utils import timezone
       from datetime import timedelta
       from zoneinfo import ZoneInfo

       last_msg = self.get_last_message()
       if not last_msg:
           return ""

       # Get user's timezone with better error handling
       user_tz = 'UTC'
       if user:
           try:
               # Try to get timezone from user profile
               if hasattr(user, 'profile') and user.profile:
                   user_tz = user.profile.timezone or 'UTC'
           except Exception as e:
               # If profile doesn't exist or any error, default to UTC
               user_tz = 'UTC'

       # Calculate time difference with proper timezone handling
       try:
           tz = ZoneInfo(user_tz)
           now = timezone.now().astimezone(tz)
           msg_time = last_msg.timestamp.astimezone(tz)
           diff = now - msg_time
       except Exception as e:
           # Fallback to UTC if timezone conversion fails
           try:
               tz = ZoneInfo('UTC')
               now = timezone.now().astimezone(tz)
               msg_time = last_msg.timestamp.astimezone(tz)
               diff = now - msg_time
           except:
               # Last resort: use aware datetimes without conversion
               now = timezone.now()
               msg_time = last_msg.timestamp
               diff = now - msg_time

       # Format the time difference
       try:
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
               return msg_time.strftime("%b %d")
       except Exception as e:
           # If all else fails, return a simple format
           return "Recently"

   def has_unread_messages(self, user):
       """Check if conversation has unread messages for user"""
       return self.messages.filter(is_read=False).exclude(sender=user).exists()

   def get_unread_count(self, user):
       """Get count of unread messages for user"""
       return self.messages.filter(is_read=False).exclude(sender=user).count()

   def is_user_admin(self, user):
       """Check if a user is an admin in this conversation"""
       if not self.is_team:
           return False
       try:
           participant = Participant.objects.get(conversation=self, user=user)
           return participant.role == 'admin'
       except Participant.DoesNotExist:
           return False

   def get_admins(self):
       """Get all admin participants in this conversation"""
       return self.participants.filter(
           participant__conversation=self,
           participant__role='admin'
       )

   def __str__(self):
       if self.is_personal_notes:
           return "Personal Notes"
       if self.is_team:
           return self.title or f"Team Conversation {self.id}"
       participants = list(self.participants.all()[:2])
       if len(participants) == 2:
           return f"{participants[0].username} & {participants[1].username}"
       return f"Conversation {self.id}"

class Participant(models.Model):
   ROLE_CHOICES = [
       ('member', 'Member'),
       ('admin', 'Admin'),
   ]

   user = models.ForeignKey(User, on_delete=models.CASCADE)
   conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
   role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
   joined_at = models.DateTimeField(auto_now_add=True)

   class Meta:
       unique_together = ('user', 'conversation')

   def __str__(self):
       return f"{self.user.username} ({self.role}) in {self.conversation.id}"

class Message(models.Model):
   MESSAGE_TYPE_CHOICES = [
       ('regular', 'Regular'),
       ('system', 'System'),
   ]

   id = models.AutoField(primary_key=True)
   conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
   sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
   content = models.TextField(blank=True)
   message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='regular')
   timestamp = models.DateTimeField(auto_now_add=True)
   is_read = models.BooleanField(default=False)
   reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
   thread_root = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='thread_replies')

   # File attachments
   attachment = models.FileField(upload_to='message_attachments/%Y/%m/%d/', null=True, blank=True)
   attachment_type = models.CharField(max_length=10, null=True, blank=True, choices=[
       ('image', 'Image'),
       ('pdf', 'PDF'),
       ('other', 'Other'),
   ])

   def get_thread_count(self):
       """Get the number of replies in this message's thread"""
       return self.thread_replies.count()

   def get_latest_thread_reply(self):
       """Get the most recent reply in this thread"""
       return self.thread_replies.order_by('-timestamp').first()

   def get_attachment_filename(self):
       """Get just the filename from the attachment path"""
       if self.attachment:
           return self.attachment.name.split('/')[-1]
       return None

   def save(self, *args, **kwargs):
       """Override save to automatically set attachment_type based on file extension"""
       if self.attachment and not self.attachment_type:
           file_ext = self.attachment.name.split('.')[-1].lower()
           if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
               self.attachment_type = 'image'
           elif file_ext == 'pdf':
               self.attachment_type = 'pdf'
           else:
               self.attachment_type = 'other'
       super().save(*args, **kwargs)

   def __str__(self):
       if self.message_type == 'system':
           return f"[SYSTEM] {self.content[:50]}"
       return f"{self.sender.username if self.sender else 'Unknown'}: {self.content[:50]}"


# Signal to auto-add new team members to existing team chats
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender='teams.TeamMembership')
def add_member_to_team_chat(sender, instance, created, **kwargs):
    """Automatically add new team members to existing team chat"""
    if created:
        from teams.models import TeamMembership

        # Get the team and user
        team = instance.team
        user = instance.user

        # Check if a team conversation already exists
        team_conversation = Conversation.objects.filter(
            team=team,
            is_team=True
        ).first()

        if team_conversation:
            # Determine if user should be admin based on team role
            is_admin = instance.role in ['Owner', 'Admin']
            participant_role = 'admin' if is_admin else 'member'

            # Add user to the conversation if not already a participant
            participant, was_created = Participant.objects.get_or_create(
                user=user,
                conversation=team_conversation,
                defaults={'role': participant_role}
            )

            # Create system message announcing the join
            if was_created:
                Message.objects.create(
                    conversation=team_conversation,
                    content=f"{user.get_full_name() or user.username} joined the conversation",
                    message_type='system',
                    sender=None
                )