# projects/forms.py
from django import forms
from django.db import models  # for Q() queries
from django.contrib.auth.models import User
from company.models import Company
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "collaborators", "companies"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # --- Collaborators field ---
        # Show all users except the current user
        self.fields["collaborators"].queryset = User.objects.exclude(
            id=user.id if user else None
        )

        # --- Companies field ---
        # Only show companies that this user owns or belongs to
        if user:
            self.fields["companies"].queryset = Company.objects.filter(
                models.Q(owner=user) | models.Q(members=user)
            ).distinct()
        else:
            self.fields["companies"].queryset = Company.objects.none()

        # --- Field Styling ---
        self.fields["name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter project name"
        })

        self.fields["description"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter project description",
            "rows": 3,
        })

        self.fields["collaborators"].widget.attrs.update({
            "class": "form-select",
            "multiple": True,
        })

        self.fields["companies"].widget.attrs.update({
            "class": "form-select",
            "multiple": True,
        })

