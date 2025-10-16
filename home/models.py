from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

class Task(models.Model):
   title = models.CharField(max_length=200)
   id = models.IntegerField(primary_key=True)
   content = models.CharField(max_length=200)
   group = models.IntegerField(default=-1)
   deadline = models.CharField(max_length=200)
   pub_date = models.CharField(max_length=200)
   color = ArrayField(models.IntegerField(), size=3) #ArrayField only works with PostgreSQL
   project = models.IntegerField()
   users = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Text(models.Model):
   id = models.IntegerField(primary_key=True)
   content = models.CharField(max_length=200)
   sender = models.IntegerField()
   receiver = models.IntegerField()
   datetime = models.DateTimeField(max_length=200)
   is_read = models.BooleanField(default=False)

class Event(models.Model):
   title = models.CharField(max_length=200)
   id = models.IntegerField(primary_key=True)
   task = models.IntegerField()
   datetime = models.DateTimeField(max_length=200)
   users = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Company(models.Model):
   id = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=200)
   email = models.EmailField(unique=True)
   phone = models.CharField(max_length=15)
   address = models.CharField(max_length=200)
   owner = models.IntegerField()
   admins = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   users = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Project(models.Model):
   id = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=200)
   description = models.CharField(max_length=300*20) #300 words 20 characters per word
   company = models.IntegerField()
   owner = models.IntegerField()
   users = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   tasks = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Team(models.Model):
   id = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=200)
   description = models.CharField(max_length=300*20) #300 words 20 characters per word
   company = models.IntegerField()
   owner = models.IntegerField()
   admins = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   users = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   projects = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   texts = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Email(models.Model):
   id = models.IntegerField(primary_key=True)
   sender = models.EmailField()
   receiver = models.EmailField()
   subject = models.CharField(max_length=200)
   content = models.CharField(max_length=1000*20) #300 words 20 characters per word
   datetime = models.DateTimeField(max_length=200)
   
class Conversation(models.Model):
   id = models.IntegerField(primary_key=True)
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
   id = models.IntegerField(primary_key=True)
   conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
   sender = models.ForeignKey(User, on_delete=models.CASCADE)
   content = models.TextField()
   timestamp = models.DateTimeField(auto_now_add=True)
   is_read = models.BooleanField(default=False)
   
