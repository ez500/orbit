from django.db import models
from django.conf import settings
#from companies.models import Company
from teams.models import Team

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="led_projects"
    )
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name="collaborating_projects",
        blank=True
    )
    #company = models.ForeignKey(
        #Company, 
        #on_delete=models.SET_NULL, 
        #null=True, 
        #blank=True,
        #related_name="projects"
    #)
    related_projects = models.ManyToManyField(
        "self", 
        blank=True, 
        symmetrical=False
    )
    clients = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def total_collaborators(self):
        return self.collaborators.count()

