from django.db import models
from django.contrib.postgres.fields import ArrayField

def default_color():
    return [0, 0, 0]

# TODO SEPARATE TASKS & CALENDAR INTO SEPARATE APP
class Task(models.Model):
   title = models.CharField(max_length=200)
   id = models.AutoField(primary_key=True)
   content = models.CharField(max_length=200)
   team = models.IntegerField(default=-1)
   deadline = models.CharField(max_length=200)
   pub_date = models.CharField(max_length=200)
   status = ArrayField(models.IntegerField(), size=3, blank=True, default=default_color) #ArrayField only works with PostgreSQL
   project = models.IntegerField(default=-1)
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

class Project(models.Model):
   id = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=200)
   description = models.CharField(max_length=300*20) #300 words 20 characters per word
   company = models.IntegerField()
   owner = models.IntegerField()
   users = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   tasks = ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Email(models.Model):
   id = models.IntegerField(primary_key=True)
   sender = models.EmailField()
   receiver = models.EmailField()
   subject = models.CharField(max_length=200)
   content = models.CharField(max_length=1000*20) #300 words 20 characters per word
   datetime = models.DateTimeField(max_length=200)

