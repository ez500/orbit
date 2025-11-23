# projects/forms.py
from django import forms
from django.db import models  # for Q() queries
from django.contrib.auth.models import User
from company.models import Company
from .models import Project, ProjectDocument
from teams.models import Team


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "collaborators", "companies", "team"]  # ✅ added team
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter project name"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter project description",
                "rows": 3
            }),
            "collaborators": forms.SelectMultiple(attrs={
                "class": "form-select"
            }),
            "companies": forms.SelectMultiple(attrs={
                "class": "form-select"
            }),
            "team": forms.Select(attrs={
                "class": "form-select"
            }),
        }

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
                models.Q(owner=user) | models.Q(memberships__user=user)
            ).distinct()
        else:
            self.fields["companies"].queryset = Company.objects.none()

        # --- Team field ---
        # Only show teams that the user belongs to or owns
        if user:
            self.fields["team"].queryset = Team.objects.filter(
            memberships__user=user
            ).distinct()
        else:
            self.fields["team"].queryset = Team.objects.none()


class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["name", "file"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Document name"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class InternalDocumentForm(forms.ModelForm):
    """
    Used for creating/editing internal CRM documents written in the editor.
    Stores HTML content in ProjectDocument.content.
    """
    class Meta:
        model = ProjectDocument
        fields = ["name", "content"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Document title"}),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 20,
                "placeholder": "Write your document here..."
            }),
        }
