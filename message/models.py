from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import uuid

# Create your models here.


# TODO INTEGRATE GEMINI INTO MESSAGES WITH EMBEDDED APPLICATION CONTEXT
class Conversation(models.Model):
   id = models.AutoField(primary_key=True)
   is_team = models.BooleanField(default=False)
   title = models.CharField(max_length=255, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   participants = models.ManyToManyField(User, through='Participant')
   
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