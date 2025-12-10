from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="company_logos/", default="default_company.png")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_companies")

    def __str__(self):
        return self.name


class CompanyMembership(models.Model):
    ROLE_CHOICES = [
        ("employee", "Employee"),
        ("mod", "Moderator"),
        ("admin", "Admin"),
        ("owner", "Owner"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_memberships")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="employee")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __str__(self):
        return f"{self.user.username} - {self.company.name} ({self.role})"


class CompanyMembershipRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __str__(self):
        return f"Request by {self.user} to join {self.company}"


class Announcement(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=200)
    content = models.TextField()
    tasks = models.ManyToManyField('dashboard.Task', blank=True, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.company.name}"
