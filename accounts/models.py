from django.db import models
from django.contrib.auth.models import User

from enum import Enum

# Create your models here.

class Profile(models.Model):
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
    connections = models.ManyToManyField('self')
    companies = models.ManyToManyField("home.Company")
    teams = models.ManyToManyField("home.Team")
    projects = models.ManyToManyField("home.Project")
    tasks = models.ManyToManyField("home.Task")
    visibility = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in Visibility],
                                  default=Visibility.PUBLIC.name)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

