from django.db import models
from django.contrib.auth.models import User

from enum import Enum

# Create your models here.

class Profile(models.Model):
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

    class Visibility(Enum):
        PUBLIC = 'Public'
        PRIVATE = 'Private'
        HIDDEN = 'Hidden'

        @property
        def public(self):
            return self == Profile.Visibility.PUBLIC

        @property
        def visible(self):
            return self != Profile.Visibility.HIDDEN

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', default='default.jpg')
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    connections = models.ManyToManyField('self', blank=True)
    theme_color = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='dark',
        blank=True,
        help_text='User interface theme preference'
    )
    accent_color = models.CharField(
        max_length=7,
        choices=ACCENT_CHOICES,
        default='#1E90FF',
        blank=True,
        help_text='Accent color for UI elements'
    )
    # Accessibility / text preference fields
    high_contrast = models.BooleanField(
        default=False,
        help_text='Enable high contrast mode for better visibility'
    )

    FONT_SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]
    font_size = models.CharField(
        max_length=10,
        choices=FONT_SIZE_CHOICES,
        default='medium',
        blank=True,
        help_text='Preferred text size'
    )

    SPACING_CHOICES = [
        ('compact', 'Compact'),
        ('normal', 'Normal'),
        ('relaxed', 'Relaxed'),
    ]
    spacing = models.CharField(
        max_length=10,
        choices=SPACING_CHOICES,
        default='normal',
        blank=True,
        help_text='Text and element spacing preference'
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        blank=True,
        help_text='User timezone for displaying times'
    )
    visibility = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in Visibility],
                                  default=Visibility.PUBLIC.name)
    last_active = models.DateTimeField(auto_now=True, help_text='Last time user was active')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_email = models.BooleanField(default=True)
    notification_web = models.BooleanField(default=True)

    # Tour/onboarding tracking
    has_completed_tour = models.BooleanField(
        default=False,
        help_text='Whether user has completed the initial guided tour'
    )

    def __str__(self):
        return self.user.username

    class Meta:
        app_label = 'accounts'

    def get_profile_data(self):
        return {
            'high_contrast': self.high_contrast,
            'font_size': self.font_size,
            'spacing': self.spacing,
            'theme_color': self.theme_color,
            'accent_color': self.accent_color
        }

    def get_online_status(self):
        """Get user's online status based on last_active time"""
        from django.utils import timezone
        from datetime import timedelta

        if not self.last_active:
            return 'offline'

        now = timezone.now()
        time_since_active = now - self.last_active

        if time_since_active < timedelta(minutes=5):
            return 'online'  # Green
        elif time_since_active < timedelta(minutes=30):
            return 'away'  # Yellow
        else:
            return 'offline'  # Gray or hidden

class ConnectionRequest(models.Model):
    from_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_requests')
    to_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Connection Request from {self.from_profile} to {self.to_profile}'
