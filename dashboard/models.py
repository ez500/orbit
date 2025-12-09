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


class DashboardWidget(models.Model):
    """Model to store user's dashboard widget configuration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_config')
    widgets = models.JSONField(default=list, blank=True)  # List of widget configurations
    layout = models.JSONField(default=dict, blank=True)  # Layout positions and sizes
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dashboard config for {self.user.username}"

    class Meta:
        verbose_name = "Dashboard Widget Configuration"
        verbose_name_plural = "Dashboard Widget Configurations"
