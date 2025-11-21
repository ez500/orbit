from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


# Create your models here.


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'


# TODO: TEST TASK AND EVENT MODELS FOR PROJECT, TEAM, AND DASHBOARD INTEGRATION
class Task(models.Model):
    STATUS = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Pending Review'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='todo')
    deadline = models.DateField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='tasks')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='tasks')
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=200, blank=True)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='events')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='events')
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title
