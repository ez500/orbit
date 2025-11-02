from django.db import models
from accounts.models import User
from teams.models import Team
from projects.models import Project
from company.models import Company
# Create your models here.

class contents(models.Model):
    users = models.ManyToManyField(User);
    teams = models.ManyToManyField(Team);
    #TODO Implement company, project, tasks, and announcements, etc
    companies = models.ManyToManyField(Company);
    project = models.ManyToManyField(Project);
    #tasks =
