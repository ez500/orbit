from django.db import models
from django.contrib.postgres.fields import ArrayField

class User(models.Model):
   username = models.CharField(max_length=200, unique=True)
   hashed_password=models.CharField(max_length=200)
   userEmail=models.EmailField(unique=True)
   userId=models.IntegerField(primary_key=True)
   #profilePicture
   connectionIds=models.IntegerField(unique=True)
   groups=ArrayField(models.IntegerField(unique=True), blank=True, default=list) #ArrayField only works with PostgreSQL
   projects=ArrayField(models.IntegerField(unique=True), blank=True, default=list) #ArrayField only works with PostgreSQL
   tasks=ArrayField(models.IntegerField(unique=True), blank=True, default=list) #ArrayField only works with PostgreSQL
   isVisible=models.BooleanField(default=True)
   isPrivate=models.BooleanField(default=False)
   acceptMessage=models.BooleanField(default=True)

class Task(models.Model):
   taskTitle=models.CharField(max_length=200)
   taskId=models.IntegerField(primary_key=True)
   taskContent=models.CharField(max_length=200)
   taskGroup=-1
   taskDeadLine=models.CharField(max_length=200)
   taskStartDate=models.CharField(max_length=200)
   taskColor=ArrayField(models.IntegerField(), size=3) #ArrayField only works with PostgreSQL
   taskProject=models.IntegerField()
   taskUsers=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Text(models.Model):
   textId=models.IntegerField(primary_key=True)
   textContent=models.CharField(max_length=200)
   textSender=models.IntegerField()
   textReceiver=models.IntegerField()
   textTime=models.TimeField(max_length=200)
   textDate=models.DateField(max_length=200)
   isRead=models.BooleanField(default=False)

class Event(models.Model):
   eventTitle=models.CharField(max_length=200)
   eventId=models.IntegerField(primary_key=True)
   eventTask=models.IntegerField()
   eventDate=models.CharField(max_length=200)
   eventTime=models.CharField(max_length=200)
   eventUsers=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Company(models.Model):
   companyId=models.IntegerField(primary_key=True)
   companyName=models.CharField(max_length=200)
   companyEmail=models.EmailField(unique=True)
   companyPhone=models.CharField(max_length=15)
   companyAddress=models.CharField(max_length=200)
   companyOwner=models.IntegerField()
   companyAdmins=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   companyUsers=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Project(models.Model):
   projectId=models.IntegerField(primary_key=True)
   projectName=models.CharField(max_length=200)
   projectDescription=models.CharField(max_length=300*20) #300 words 20 characters per word
   projectCompany=models.IntegerField()
   projectOwner=models.IntegerField()
   projectUsers=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   projectTasks=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Team(models.Model):
   teamId=models.IntegerField(primary_key=True)
   teamName=models.CharField(max_length=200)
   teamDescription=models.CharField(max_length=300*20) #300 words 20 characters per word
   teamCompany=models.IntegerField()
   teamOwner=models.IntegerField()
   teamAdmins=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   teamUsers=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   teamProjects=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL
   teamTexts=ArrayField(models.IntegerField(), blank=True, default=list) #ArrayField only works with PostgreSQL

class Email(models.Model):
   emailId=models.IntegerField(primary_key=True)
   emailSender=models.EmailField()
   emailReceiver=models.EmailField()
   emailSubject=models.CharField(max_length=200)
   emailContent=models.CharField(max_length=1000*20) #300 words 20 characters per word
   emailTime=models.TimeField(max_length=200)
   emailDate=models.DateField(max_length=200)

# Create your models here.
