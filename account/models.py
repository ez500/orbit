from django.db import models

from home.models import Company, Team, Project, Task

# Create your models here.

class Profile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    userId = models.IntegerField(primary_key=True)
    profilePicture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    connections = models.ManyToManyField('self')
    companies = models.ManyToManyField(Company)
    teams = models.ManyToManyField(Team)
    projects = models.ManyToManyField(Project)
    tasks = models.ManyToManyField(Task)
    isVisible = models.BooleanField(default=True)
    isPrivate = models.BooleanField(default=False)

