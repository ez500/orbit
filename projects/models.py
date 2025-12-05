from django.db import models
from django.contrib.auth.models import User
from company.models import Company
from django.utils import timezone
from teams.models import Team


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    lead = models.ForeignKey(
        User, related_name="led_projects", on_delete=models.CASCADE
    )
    collaborators = models.ManyToManyField(
        User, related_name="collaborative_projects", blank=True
    )
    # TODO: ASSOCIATE WITH ONLY ONE COMPANY OR ONE TEAM, IMPLEMENT JAVASCRIPT OR DROPDOWN LOGIC
    companies = models.ManyToManyField(
        Company, related_name="projects", blank=True
    )

    # ✅ New team field
    team = models.ForeignKey(
        Team,
        related_name="projects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: associate this project with a team.",
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Auto-update the `updated_at` field and sync team members."""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

        # ✅ Automatically add all team members as collaborators
        if self.team:
            for member in self.team.members.all():
                self.collaborators.add(member)

    def __str__(self):
        return self.name


class ProjectDocument(models.Model):
    project = models.ForeignKey(
        "Project", related_name="documents", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="project_docs/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.project.name})"
