from django.db import models
from django.contrib.auth.models import User
from company.models import Company
from django.utils import timezone


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Relationships
    lead = models.ForeignKey(User, related_name="led_projects", on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(User, related_name="collaborative_projects", blank=True)
    companies = models.ManyToManyField(Company, related_name="projects", blank=True)

    # Timestamp fields (non-migrating safe)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Auto-update the `updated_at` field."""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
