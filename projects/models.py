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
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    file = models.FileField(
        upload_to="project_docs/",
        null=True,
        blank=True,
        help_text="Uploaded file. Leave empty if creating internal document."
    )

    content = models.TextField(
        null=True,
        blank=True,
        help_text="Internal CRM document stored as HTML."
    )

    TYPE_CHOICES = [
        ("file", "Uploaded File"),
        ("internal", "Internal CRM Document"),
    ]

    doc_type = models.CharField(
        default="file",
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="Document type: uploaded or created internally."
    )

    def __str__(self):
        return f"{self.name} ({self.project.name})"
