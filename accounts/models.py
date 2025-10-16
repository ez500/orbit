from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    class Meta:
        app_label = 'accounts'
        
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    ]

    ACCENT_CHOICES = [
        ('#1E90FF', 'Blue'),
        ('#32CD32', 'Green'),
        ('#9370DB', 'Purple'),
        ('#FF4500', 'Red Orange'),
        ('#FFD700', 'Gold'),
        ('#FF69B4', 'Pink'),
        ('#20B2AA', 'Teal'),
        ('#FF8C00', 'Dark Orange'),
    ]

    VISIBILITY_CHOICES = [
        ('public', 'Public - Anyone can view your profile'),
        ('connections', 'Connections Only - Only your connections can view your profile'),
        ('private', 'Private - Only you can view your profile'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    connections = models.ManyToManyField('self')
    companies = models.ManyToManyField("home.Company")
    teams = models.ManyToManyField("home.Team")
    projects = models.ManyToManyField("home.Project")
    tasks = models.ManyToManyField("home.Task")
    is_visible = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
    theme_color = models.CharField(max_length=20, choices=THEME_CHOICES, default='default')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    accent_color = models.CharField(max_length=7, choices=ACCENT_CHOICES, default='#1E90FF')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    notification_email = models.BooleanField(default=True)
    notification_web = models.BooleanField(default=True)

