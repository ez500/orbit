from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


# Create your models here.


class Task(models.Model):
    STATUS = [
        ('todo', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Pending Review'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='todo')
    deadline = models.DateField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    id = models.IntegerField(primary_key=True)
    task = models.IntegerField()
    datetime = models.DateTimeField(max_length=200)
    users = ArrayField(models.IntegerField(), blank=True, default=list)
