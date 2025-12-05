from django.db import models
from django.contrib.auth.models import User
from company.models import Company
from django.utils import timezone
from teams.models import Team


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # DO NOT REMOVE (used by other apps)
    lead = models.ForeignKey(
        User, related_name="led_projects", on_delete=models.CASCADE
    )
    collaborators = models.ManyToManyField(
        User, related_name="collaborative_projects", blank=True
    )

    companies = models.ManyToManyField(Company, related_name="projects", blank=True)

    team = models.ForeignKey(
        Team,
        related_name="projects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    # ------------------------------------------------------------
    # NEW HELPERS FOR ROLE SYSTEM
    # ------------------------------------------------------------
    def get_lead_membership(self):
        return self.memberships.filter(role="Lead").first()

    def get_managers(self):
        return self.memberships.filter(role="Manager")

    def get_members(self):
        return self.memberships.filter(role="Member")

    def get_role(self, user):
        m = self.memberships.filter(user=user).first()
        return m.role if m else None

    # ------------------------------------------------------------
    # AUTO-SYNC: Lead + Collaborators ↔ ProjectMembership
    # ------------------------------------------------------------
    def sync_roles(self):
        """
        Ensures:
        - Lead always has a ProjectMembership(role="Lead")
        - Managers & Members are always in collaborators
        - Lead is NOT added to collaborators
        - Removal from membership removes from collaborators
        """

        # 1. Sync Lead
        lead_mem = self.memberships.filter(user=self.lead).first()
        if not lead_mem:
            ProjectMembership.objects.create(
                user=self.lead,
                project=self,
                role="Lead"
            )
        else:
            if lead_mem.role != "Lead":
                lead_mem.role = "Lead"
                lead_mem.save()

        # 2. Ensure Managers/Members are collaborators
        for mem in self.memberships.all():
            if mem.role in ["Manager", "Member"]:
                self.collaborators.add(mem.user)

        # 3. Remove collaborators who no longer have membership
        collaborator_ids = set(self.collaborators.values_list("id", flat=True))
        membership_ids = set(
            self.memberships.exclude(role="Lead").values_list("user_id", flat=True)
        )

        to_remove = collaborator_ids - membership_ids
        if to_remove:
            self.collaborators.remove(*to_remove)

    # Override save to trigger sync
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

        # Only sync AFTER project exists
        if self.pk:
            self.sync_roles()

class ProjectDocument(models.Model):
    project = models.ForeignKey(
        "Project", related_name="documents", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

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

class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ("Lead", "Project Lead"),
        ("Manager", "Project Manager"),
        ("Member", "Project Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.username} in {self.project.name} ({self.role})"

    # ------------------------------------------------------------
    # Auto-sync on role change
    # ------------------------------------------------------------
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.project.sync_roles()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.project.sync_roles()
