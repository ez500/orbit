from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    company = models.ForeignKey("company.Company",
                                on_delete=models.SET_NULL, blank=True, null=True, related_name="teams")

    # Related name gives you: request.user.teams.all()
    members = models.ManyToManyField(
        User,
        through="TeamMembership",
        related_name="teams",
    )

    def __str__(self):
        return self.name

    def get_lead(self):
        return self.memberships.filter(role="Lead").first()


class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    ROLE_CHOICES = [
        ("Lead","Team Lead"),
        ("Manager","Team Manager"),
        ("Member","Team Member"),

    ]

    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default="Member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "team")

    def __str__(self):
        return f"{self.user} in {self.team} ({self.role or 'Member'})"

class TeamDocument(models.Model):
    TYPE_CHOICES = [
        ("file", "Uploaded File"),
        ("internal", "Internal Document"),
        ("link", "External Link"),
    ]

    team = models.ForeignKey(
        "Team",
        related_name="documents",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="file")

    file = models.FileField(upload_to="team_docs/", blank=True, null=True)

    content = models.TextField(blank=True, null=True)

    external_url = models.URLField(blank=True, null=True)

    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.team.name})"
