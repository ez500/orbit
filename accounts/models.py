from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userId = models.IntegerField(primary_key=True)
    profilePicture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    connections = models.ManyToManyField('self')
    companies = models.ManyToManyField("home.Company")
    teams = models.ManyToManyField("home.Team")
    projects = models.ManyToManyField("home.Project")
    tasks = models.ManyToManyField("home.Task")
    isVisible = models.BooleanField(default=True)
    isPrivate = models.BooleanField(default=False)

