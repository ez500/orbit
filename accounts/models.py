from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    connections = models.ManyToManyField('self')
    companies = models.ManyToManyField("home.Company")
    teams = models.ManyToManyField("home.Team")
    projects = models.ManyToManyField("home.Project")
    tasks = models.ManyToManyField("home.Task")
    is_visible = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

