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


class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=50, blank=True)  # "Owner", "Member", etc.
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "team")

    def __str__(self):
        return f"{self.user} in {self.team} ({self.role or 'Member'})"
