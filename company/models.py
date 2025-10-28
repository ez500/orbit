from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=80)
    description = models.CharField(blank=True, max_length=200)
    profile_picture = models.ImageField(upload_to='company_profile_pictures', default='default_company.png')
    email = models.EmailField(blank=True, unique=True)
    website = models.URLField(blank=True)
    phone = models.CharField(blank=True)
    location = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_set')
    members = models.ManyToManyField(User, through='CompanyMembership')

    def __str__(self):
        return self.name


class CompanyMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True)  # "Owner", "Admin", "Member", etc.
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __str__(self):
        return f"{self.user} in {self.company} ({self.role or 'Member'})"

