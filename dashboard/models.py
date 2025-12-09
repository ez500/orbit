from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone


# Create your models here.


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    announcement = models.ForeignKey(
        "company.Announcement",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True
    )

    # TODO ADD OTHER MODELS TO NOTIFICATIONS

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
    pub_date = models.DateTimeField(auto_now_add=True)
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
    pub_date = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='events')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='events')
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title


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


class InsightSuggestion(models.Model):
    TYPE_CHOICES = [
        ("create_task", "Create Task"),
        ("create_event", "Create Event"),
        ("create_announcement", "Create Announcement"),
        ("send_message", "Send Message"),
        ("send_email", "Send Email"),
        ("general_insight", "Insight"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="insight_suggestions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    suggestion_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    raw_data = models.JSONField(encoder=DjangoJSONEncoder, default=dict)
    saved = models.BooleanField(default=False)
    executed = models.BooleanField(default=False)
    saved_at = models.DateTimeField(null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    batch_id = models.CharField(max_length=100, null=True, blank=True)

    # TODO SAVED AND EXECUTED SUGGESTIONS VIEW SECTION ON ORBIT INSIGHTS PAGE
    def mark_saved(self):
        self.saved = True
        self.saved_at = timezone.now()
        self.save()

    def mark_executed(self):
        self.executed = True
        self.saved = False
        self.executed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.id} ({self.user.username} - {self.suggestion_type})"

